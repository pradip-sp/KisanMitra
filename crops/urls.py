from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static
# from .views import ai_page, ai_followup


urlpatterns = [
    path("",views.index,name="index"),
    path("index",views.index,name="index"),
    path("crops",views.crops,name="crop"),
    path("crops/<int:id>/", views.crop_detail, name="crop_detail"),
    path("fertilizer",views.fertilizers,name="fertilizers"),
    path("fertilizer/<int:id>/", views.fertilizer_detail, name="fertilizer_detail"),
    path("pesticides",views.pesticides,name="pesticides"),
    path("pesticides/<int:id>/", views.pesticides_detail, name="pesticides_detail"),
    path("about",views.about,name="about"),
    path("contact/",views.contact,name="contact"),
    path("subscribe/", views.subscribe, name="subscribe"),

]
