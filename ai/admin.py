from django.contrib import admin
from ai.models import CropQuery

# Register your models here.
@admin.register(CropQuery)
class CropQueryAdmin(admin.ModelAdmin):
    list_display = ["id", "farmer_name", "location", "created_at"]
    readonly_fields = ["ai_response", "created_at"]
    search_fields = ["farmer_name", "location", "question_text"]
