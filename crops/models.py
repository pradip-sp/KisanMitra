from django.db import models
from tinymce.models import HTMLField
from cloudinary.models import CloudinaryField

# Create your models here.
class Signup(models.Model):
    username=models.CharField(max_length=100)
    email=models.CharField(max_length=100)
    password=models.CharField(max_length=100)
    confirmpassword=models.CharField(max_length=100)


    def __str__(self):
        return self.username


class Crop(models.Model):
    name = models.CharField(max_length=100)
    image = CloudinaryField('photo')
    card_desc = models.TextField(default="")
    description = HTMLField()

    def __str__(self):
        return self.name


class Fertilizer(models.Model):
    name = models.CharField(max_length=100)
    image = CloudinaryField('photo')
    # image = models.ImageField(upload_to='Fertilizer/')
    card_desc = models.TextField(default="")
    description = HTMLField()

    def __str__(self):
        return self.name

class Pesticides(models.Model):
    name = models.CharField(max_length=100)
    image = CloudinaryField('photo')
    # image = models.ImageField(upload_to='Pesticides/')
    card_desc = models.TextField(default="")
    description = HTMLField()

    def __str__(self):
        return self.name
    
class Contact(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField()
    number = models.CharField(max_length=20)
    desc = models.TextField()
    date_by = models.DateField()

    def __str__(self):
        return self.name

class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

