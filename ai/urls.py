from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import ai_page, ai_followup


urlpatterns = [
path("",views.ai_page,name="ai-page"),
path("<int:pk>/ask/", ai_followup, name="ai-followup"),
    
]