import json
from ai.models import CropQuery
from datetime import datetime
from django.shortcuts import render, redirect
from .forms import CropQueryForm
from .ai_service import analyze_crop, ask_followup
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import requests

# Create your views here.

# ai page 
def ai_page(request):
    """
    Website ke menu me 'AI' button isi view par le jayega.
    GET  -> khali form dikhao
    POST -> photo+sawaal save karo, AI se jawaab lo, result dikhao
    """
    result = None

    if request.method == "POST":
        form = CropQueryForm(request.POST, request.FILES)
        if form.is_valid():
            crop_query = form.save()  # photo yahin save ho jaati hai

            ai_answer = analyze_crop(crop_query.photo, crop_query.question_text)
            crop_query.ai_response = ai_answer
            crop_query.save(update_fields=["ai_response"])

            result = crop_query
            form = CropQueryForm()  # naya khali form agli query ke liye
    else:
        form = CropQueryForm()

    return render(request, "ai_page.html", {"form": form, "result": result})


@require_POST
def ai_followup(request, pk):
    """
    Isi photo/query par naya follow-up sawaal poochne ke liye (AJAX se call hota hai).
    Photo dobara bhejne ki zaroorat nahi - AI ko pichli baatcheet yaad rehti hai.

    POST body (JSON): {"question": "..."}
    Response (JSON): {"answer": "..."} ya {"error": "..."}
    """
    crop_query = get_object_or_404(CropQuery, pk=pk)

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, TypeError):
        return JsonResponse({"error": "Galat request format."}, status=400)

    question = (data.get("question") or "").strip()
    if not question:
        return JsonResponse({"error": "Kripya koi sawaal likhein."}, status=400)

    answer, error = ask_followup(crop_query, question)
    if error:
        return JsonResponse({"error": error}, status=200)  # user-friendly message, page par dikhega

    return JsonResponse({"answer": answer})
