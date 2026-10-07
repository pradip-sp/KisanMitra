from django import forms
from .models import CropQuery


class CropQueryForm(forms.ModelForm):
    class Meta:
        model = CropQuery
        fields = ["photo", "question_text", "farmer_name", "location"]
        widgets = {
            "photo": forms.ClearableFileInput(attrs={
                "accept": "image/*",
                "class": "form-control",
                "id": "id_photo",
                "style": "display:none;",  # ye asli field hai, hidden rahegi - JS ise bharega
            }),
            "question_text": forms.Textarea(attrs={
                "rows": 3,
                "placeholder": "Apna sawaal likhein (optional) - jaise 'iski patti pili kyun ho rahi hai'",
                "class": "form-control",
            }),
            "farmer_name": forms.TextInput(attrs={
                "placeholder": "Aapka naam (optional)",
                "class": "form-control",
            }),
            "location": forms.TextInput(attrs={
                "placeholder": "Gaon/Jagah (optional)",
                "class": "form-control",
            }),
        }
        labels = {
            "photo": "Fasal ki photo",
            "question_text": "Sawaal",
            "farmer_name": "Naam",
            "location": "Jagah",
        }
