from django.db import models


class CropQuery(models.Model):
    """
    Ek entry = kisan ne ek photo + sawaal bheja, aur AI ne jawaab diya.
    """
    photo = models.ImageField(upload_to="crop_photos/%Y/%m/%d/")
    question_text = models.TextField(
        blank=True,
        help_text="Kisan ka sawaal, jaise 'iski patti pili kyun ho rahi hai'",
    )
    ai_response = models.TextField(blank=True, help_text="AI ka jawaab (Hindi me)")
    created_at = models.DateTimeField(auto_now_add=True)
    # Isi photo par baad me pooche gaye follow-up sawaal-jawaab yaha store hote hain
    # Format: [{"role": "user", "content": "..."}, {"role": "assistant", "content": "..."}, ...]
    conversation = models.JSONField(default=list, blank=True)
    
    # optional: agar aapko location/farmer id track karna ho
    farmer_name = models.CharField(max_length=150, blank=True)
    location = models.CharField(max_length=150, blank=True)

    def __str__(self):
        return f"Query #{self.id} - {self.created_at:%Y-%m-%d %H:%M}"

    class Meta:
        ordering = ["-created_at"]