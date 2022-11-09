from django.db import models
from secrets import token_urlsafe


def newid():
    return token_urlsafe(10)


class Lost(models.Model):
    id = models.CharField("Unique ID of lost item",
                          max_length=16, primary_key=True, default=newid)

    user_id = models.CharField("User uid", max_length=20)

    user_name = models.CharField("User name", max_length=100)

    title = models.CharField("Title of Lost Item", max_length=50)

    description = models.CharField(
        "Short Description of Lost Item", max_length=300, default=None, blank=True, null=True)

    created = models.DateTimeField("Post Created At", auto_now_add=True)

    location = models.CharField(
        "location where item was lost", max_length=100, default=None, blank=True, null=True)

    lostDate = models.DateTimeField(
        "Date when item was lost", default=None, blank=True, null=True)

    contactEmail = models.EmailField(
        "Email of owner", max_length=50, default=None, blank=True, null=True)

    contactPhone = models.CharField(
        "Phone number of owner", max_length=10, default=None, blank=True, null=True)

    image = models.CharField(
        "Image of lost item", max_length=300, default=None, blank=True, null=True)

    found = models.BooleanField("Item found or not", default=False)

    tag = models.ManyToManyField("tag.Tag", related_name="lost")
