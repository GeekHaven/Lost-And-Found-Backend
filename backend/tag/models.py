from django.db import models
from secrets import token_urlsafe


def newid():
    return token_urlsafe(10)


class Tag(models.Model):
    id = models.CharField("Unique ID of tag", max_length=16,
                          primary_key=True, default=newid)
    name = models.CharField("Tag name", max_length=32)
    img = models.CharField("tag image", max_length=300)
