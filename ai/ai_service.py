"""
Ye file kisi bhi AI provider (Gemini, Anthropic, OpenAI, Grok, wagera) ko
LiteLLM ke through call karti hai - kaunsa provider use karna hai ye
settings.AI_MODEL se decide hota hai.

Provider badalna ho to bas .env me AI_MODEL ki value badal dein aur
us provider ki API key set kar dein - code me KUCH bhi badalne ki
zaroorat nahi.

Examples (.env me):
    AI_MODEL=gemini/gemini-3.6-flash       + GEMINI_API_KEY=...
    AI_MODEL=anthropic/claude-sonnet-5     + ANTHROPIC_API_KEY=...
    AI_MODEL=openai/gpt-4o                 + OPENAI_API_KEY=...
    AI_MODEL=xai/grok-2-vision-latest      + XAI_API_KEY=...

LiteLLM khud hi sahi API key environment variable (jo provider ke naam se
match kare) uठा leta hai - hume manually pass karne ki zaroorat nahi.
"""
import base64
import io
import logging

from django.conf import settings
from PIL import Image
from litellm import completion
litellm.verbose = False

try:
    import pillow_heif
    pillow_heif.register_heif_opener()  # HEIC (iPhone) photos ke liye
except ImportError:
    pillow_heif = None

logger = logging.getLogger(__name__)

MAX_DIMENSION = 1568

SYSTEM_PROMPT = """Tum ek krishi visheshagya (agriculture expert) AI ho jo Bharat ke
kisano ki madad karte ho. Kisan tumhe apni fasal (crop) ki photo aur ek sawaal bhejega.

Tumhara jawaab hamesha:
1. GREETING me राम राम किसान भाई! aur kuchh acha sa line apne se add kar dena
2. Saral, seedhi Hindi me ho (mushkil English/technical words na use karo)
3. Chhote-chhote points me ho, taaki mobile par padhna aasan ho
4. In cheezo ko cover kare (jo bhi relevant ho):
   - Fasal/paudhe ki pehchaan
   - Agar koi bimari ya keet (pest) dikh raha hai to uska naam
   - Kya karna chahiye (ilaj/upay) - practical aur sasta upay pehle bataye
   - Agar photo se sahi jaankari nahi mil pa rahi, to saaf bata do aur
     bataye ki behtar photo kaise lein (paas se, achi roshni me, patti/tana/jad dikhaye)

Kabhi bhi jhooti ya andaazi jaankari mat do agar tumhe pakka pata nahi hai -
kisan ki fasal aur paisa dono is jaankari par depend karte hain."""

DEFAULT_QUESTION = (
    "Is fasal ki photo dekhkar bataiye ki ye kaunsi fasal hai aur "
    "iski sehat kaisi hai. Agar koi bimari ya keet dikh raha ho to bhi bataiye."
)

# GREETING = "🙏 राम राम किसान भाई! 🙂\n\n"


def _encode_image(image_field):
    """Photo ko base64 JPEG me convert karta hai (format/size normalize karne ke liye)"""
    image_field.open("rb")
    try:
        raw_bytes = image_field.read()
    finally:
        image_field.close()

    try:
        img = Image.open(io.BytesIO(raw_bytes))
        img = img.convert("RGB")
        img.thumbnail((MAX_DIMENSION, MAX_DIMENSION))

        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        processed_bytes = buffer.getvalue()
    except Exception:
        logger.exception("Image process nahi ho payi")
        return None

    return base64.b64encode(processed_bytes).decode("utf-8")


def _call_ai(messages):
    """
    Common LLM call + error handling. messages: poori conversation list.
    Return: (answer_text, error_text) - dono me se ek hamesha None hoga.
    """
    try:
        response = completion(model=settings.AI_MODEL, max_tokens=2048, messages=messages)
        choice = response.choices[0]
        answer = (choice.message.content or "").strip()

        if choice.finish_reason == "length":
            # Jawaab beech me kat gaya - user ko clue mil jaye
            logger.warning("AI ka jawaab max_tokens ki wajah se kat gaya")
            answer += "\n\n(...jawaab yahi tak seemit hai, aage jaan-ne ke liye dobara sawaal poochein)"

        if not answer:
            return "AI se koi jawaab nahi mila, dobara koshish karein.", None

        return answer, None

    except Exception as e:
        logger.exception("AI provider (%s) me error", settings.AI_MODEL)
        error_str = str(e)
        lower = error_str.lower()

        if "api key" in lower or "authentication" in lower or "401" in error_str:
            msg = "⚠️ API key sahi nahi hai. Server settings me API key check karein."
        elif "credit" in lower or "quota" in lower or "429" in error_str or "resource_exhausted" in lower:
            msg = "⚠️ Credits/free-limit khatam ho gayi hai. Thodi der baad ya provider badal kar try karein."
        elif "400" in error_str or "invalid" in lower:
            msg = "⚠️ Photo ya sawaal ke format me dikkat hai. Dobara try karein."
        else:
            msg = f"⚠️ AI service me error aaya. ({error_str[:120]})"
        return None, msg


def analyze_crop(image_field, question_text=""):
    """
    Pehli baar photo bhejne par call hota hai.
    image_field: Django ImageField/FieldFile (jo already save ho chuki ho)
    question_text: kisan ka likha hua sawaal (optional)

    Return: AI ka Hindi jawaab (string)
    """
    b64_image = _encode_image(image_field)
    if b64_image is None:
        return (
            "⚠️ Ye photo khul nahi payi (format support nahi ho raha ya file "
            "kharaab hai). Kripya ek JPEG ya PNG photo dobara upload karein."
        )

    user_text = question_text.strip() if question_text and question_text.strip() else DEFAULT_QUESTION

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": user_text},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}},
            ],
        },
    ]

    answer, error = _call_ai(messages)
    return answer if answer else error


def ask_followup(crop_query, new_question):
    """
    Isi photo/query par ek naya sawaal poochne ke liye - photo dobara
    bhejne ki zaroorat nahi, AI ko pichli poori baatcheet yaad rehti hai.

    crop_query: CropQuery model instance (jisme photo, pehla sawaal-jawaab,
                aur ab tak ki conversation history hai)
    new_question: kisan ka naya sawaal (text)

    Return: (answer, error) - success par error None, fail par answer None
    """
    new_question = (new_question or "").strip()
    if not new_question:
        return None, "⚠️ Kripya koi sawaal likhein."

    b64_image = _encode_image(crop_query.photo)
    if b64_image is None:
        return None, "⚠️ Purani photo nahi mil payi, kripya nayi photo bhejein."

    first_question = crop_query.question_text.strip() or DEFAULT_QUESTION

    # Poori conversation rebuild karo: pehla photo+sawaal+jawaab, fir baad ke sab sawaal-jawaab
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "user",
            "content": [
                {"type": "text", "text": first_question},
                {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"}},
            ],
        },
        {"role": "assistant", "content": crop_query.ai_response},
    ]
    for turn in crop_query.conversation:
        messages.append(turn)

    messages.append({"role": "user", "content": new_question})

    answer, error = _call_ai(messages)
    if error:
        return None, error

    # Naya sawaal-jawaab conversation history me save karo
    crop_query.conversation.append({"role": "user", "content": new_question})
    crop_query.conversation.append({"role": "assistant", "content": answer})
    crop_query.save(update_fields=["conversation"])

    return answer, None
