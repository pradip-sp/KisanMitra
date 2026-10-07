from django.contrib import admin
from crops.models import Contact , Crop, Subscriber, Fertilizer, Pesticides

# Register your models here.
admin.site.register([Contact,Crop, Subscriber, Fertilizer, Pesticides])
