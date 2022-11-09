from django.db import models
from secrets import token_urlsafe


def newid():
    return token_urlsafe(10)

# Create your models here.


class Found(models.Model):
    id = models.CharField("Unique ID of lost item",
                          max_length=16, primary_key=True, default=newid)
    user_id = models.CharField("User uid", max_length=20)
    user_name = models.CharField("User name", max_length=100)
    title = models.CharField("Title of Found Item", max_length=50)
    description = models.CharField(
        "Short description of found item", max_length=300, default=None, blank=True, null=True)
    created = models.DateTimeField("Post Created At", auto_now_add=True)
    location = models.CharField(
        "location where item was found", max_length=100, default=None, blank=True, null=True)
    foundDate = models.DateTimeField(
        "Date when item was lost", default=None, blank=True, null=True)
    contactEmail = models.EmailField(
        "Email of finder", max_length=50, default=None, blank=True, null=True)
    contactPhone = models.CharField(
        "Phone number of finder", max_length=10, default=None, blank=True, null=True)
    image = models.CharField(
        "Image of founded item", max_length=300, default=None, blank=True, null=True)
    ownerFound = models.BooleanField("Item owner found or not", default=False)
    tag = models.ManyToManyField("tag.Tag", related_name="found")
