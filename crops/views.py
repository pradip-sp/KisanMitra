import json
from django.contrib import messages
from crops.models import Signup, Contact, Crop, Subscriber, Fertilizer, Pesticides
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
# from .forms import CropQueryForm
# from .ai_service import analyze_crop, ask_followup
from django.views.decorators.http import require_POST
from django.http import JsonResponse
import requests
from django.shortcuts import render
# Create your views here.


def index(request):
    crops = Crop.objects.all()[:6]
    fertilizers = Fertilizer.objects.all()[:6]
    pesticides = Pesticides.objects.all()[:6]
    return render(request, "index.html", {
        "crops": crops,
        "fertilizers":fertilizers,
        "pesticides":pesticides,
        })

# Crop cards
def crops(request):
    crops = Crop.objects.all()
    #search ke liye add kiya gya hai
    if request.method=="GET":
        st=request.GET.get('search')
        if st!=None:
            crops = Crop.objects.filter(name__icontains=st)
    data={
        'crops': crops
    }
    return render(request, "crop.html",data)

# Crop detail
def crop_detail(request, id):
    crop = get_object_or_404(Crop, id=id)
    return render(request, "crop_detail.html", {"crop": crop})

# Fertilizer cards
def fertilizers(request):
    fertilizers = Fertilizer.objects.all()
    #search ke liye add kiya gya hai
    if request.method=="GET":
        st=request.GET.get('search')
        if st!=None:
            fertilizers = Fertilizer.objects.filter(name__icontains=st)
    data={
        'fertilizers': fertilizers
    }
    return render(request, "fertilizer.html",data)

# Fertilizer detail
def fertilizer_detail(request, id):
    fertilizer = get_object_or_404(Fertilizer, id=id)
    return render(request, "fertilizer_detail.html", {"fertilizer": fertilizer})

# Pesticides cards
def pesticides(request):
    pesticides = Pesticides.objects.all()
    #search ke liye add kiya gya hai
    if request.method=="GET":
        st=request.GET.get('search')
        if st!=None:
            pesticides = Pesticides.objects.filter(name__icontains=st)
    data={
        "pesticides": pesticides
    }
    return render(request, "pesticides.html",data)

# Pesticides detail
def pesticides_detail(request, id):
    pesticides = get_object_or_404(Pesticides, id=id)
    return render(request, "pesticides_detail.html", {"pesticides": pesticides})


def about(request):
    return render(request,"about.html")

def contact(request):
    if request.method == "POST":
        name = request.POST.get('name')
        email = request.POST.get('email')
        number = request.POST.get('number')
        desc = request.POST.get('desc')
        
        contact = Contact(name=name,email=email,number=number,desc=desc,date_by=datetime.today())
        contact.save()
        messages.success(request, "Your message has been submitted successfully!")

    return render(request,"contact.html")


def subscribe(request):
    if request.method == "POST":
        email = request.POST.get("email")

        if email:
            Subscriber.objects.get_or_create(email=email)
            messages.success(request, "You have subscribed successfully!")

        return redirect("index")