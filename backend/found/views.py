from django.db.models import Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from django import forms
from django.contrib.postgres.aggregates import ArrayAgg
from django.conf import settings
import pathlib
from secrets import token_urlsafe
import os
from PIL import Image

from .models import Found
from tag.models import Tag


class NewItemForm(forms.Form):
    title = forms.CharField(max_length=50, strip=True)
    description = forms.CharField(max_length=300, strip=True, required=False)
    location = forms.CharField(max_length=100, required=False, strip=True)
    foundDate = forms.DateTimeField(required=False)
    contactEmail = forms.EmailField(required=False)
    contactPhone = forms.CharField(max_length=10)
    tagIds = forms.CharField(max_length=300, required=False, strip=True)


multiSelectedCols = [
    "id",
    "title",
    "description",
    "location",
    "foundDate",
    "image",
]

selectedCols = [
    "id",
    "user_id",
    "user_name",
    "title",
    "description",
    "created",
    "location",
    "foundDate",
    "contactPhone",
    "contactEmail",
    "image",
    "ownerFound"
]


def latestFound(req):
    if (req.method != "GET"):
        return JsonResponse({"status": False, "error": "Method not allowed"}, status=405)

    page_size = req.GET.get("pagesize")
    page_number = req.GET.get("pagenumber")
    order = req.GET.get("order")
    query = req.GET.get("q")
    tag_id = req.GET.get("tag")

    if not page_size:
        page_size = 20
    if not page_number:
        page_number = 1

    founditemsquery = Found.objects.filter(ownerFound=False)

    if query:
        founditemsquery = founditemsquery.filter(Q(title__icontains=query) | Q(
            description__icontains=query) | Q(location__icontains=query))

    if tag_id:
        tag_id = tag_id.split(";")
        founditemsquery = founditemsquery.filter(tag__id__in=tag_id)

    founditems = founditemsquery.order_by(
        "created" if order == "ascending" else "-created").values(*multiSelectedCols)
    paginated = Paginator(list(founditems), page_size)
    curr_page = paginated.get_page(page_number)

    res = {
        "status": True,
        "class": "found",
        "data": curr_page.object_list,
        "page_size": len(curr_page.object_list),
        "has_next_page": curr_page.has_next(),
        "next_page_number": curr_page.next_page_number() if curr_page.number < paginated.num_pages else False,
        "total_pages": paginated.num_pages,
        "total_items": paginated.count,
    }

    return JsonResponse(res)


def getItem(req, id):
    """
    URI looks like: /found/<id>
    """
    if req.method != "GET":
        return JsonResponse({"status": False, "error": "Method not allowed"}, status=405)

    item = Found.objects.filter(id__exact=id).values(
        *selectedCols).annotate(tag=ArrayAgg("tag__name")).first()
    if item == None:
        return JsonResponse({"status": False, "error": "Item not found"}, status=404)
    return JsonResponse({
        "status": True,
        "class": "found",
        "data": item
    })


def newItem(req):
    if not req.authenticated:
        return req.unauthorisedResponse

    if req.method != "POST":
        return JsonResponse({"status": False, "error": "Method not allowed"}, status=405)
    img_file = req.FILES.get('image', None)
    file_url = None
    if img_file and img_file.size < 10485760:  # 10MB
        file_ext = pathlib.Path(img_file.name).suffix
        if (file_ext in ['.jpg', '.png', '.jpeg']):
            img = Image.open(img_file)
            # Max size of Image allowed -> 1024x1024 pixels
            img.thumbnail((1024, 1024))
            filename = req.auth_user["uid"] + \
                '-' + token_urlsafe(10) + file_ext

            img.save(os.path.join(
                settings.MEDIA_ROOT[0], filename), format=img.format)

            file_url = 'http://%s/img/%s' % (
                req.META["HTTP_HOST"], filename)

    form = NewItemForm(req.POST)
    if form.is_valid():
        newFound = Found.objects.create(
            user_id=req.auth_user["uid"],
            user_name=req.auth_user["name"],
            title=form.cleaned_data["title"],
            description=form.cleaned_data["description"],
            location=form.cleaned_data["location"],
            foundDate=form.cleaned_data["foundDate"],
            contactEmail=form.cleaned_data["contactEmail"],
            contactPhone=form.cleaned_data["contactPhone"],
            image=file_url,
        )
        tagsIdArray = form.cleaned_data["tagIds"].split(";")
        tags = Tag.objects.filter(id__in=tagsIdArray).all() or []
        newFound.tag.set(list(tags))
        return JsonResponse({
            "status": True,
            "class": "found",
            "data": {
                "itemId": newFound.id
            }
        }, status=201)
    return JsonResponse({"status": False, "error": "Invalid Form Data"}, status=400)


def markUserFound(req):
    if not req.authenticated:
        return req.unauthorisedResponse
    if req.method != "POST":
        return JsonResponse({"status": False, "error": "Method not allowed"}, status=405)

    foundItem = Found.objects.filter(id=req.jsonbody(
        req).get("id"), user_id=req.auth_user["uid"]).first()
    if not foundItem:
        return JsonResponse({"status": False, "error": "Item not found"}, status=404)

    foundItem.found = True
    foundItem.save()

    return JsonResponse({
        "status": True
    })

# to get all item from a user


def getItemOfUser(req, user_id):
    """
    URI looks like: /found/user/<user_id>
    """
    if req.method != "GET":
        return JsonResponse({"status": False, "error": "Method not allowed"}, status=405)
    item = list(Found.objects.filter(
        user_id__iexact=user_id) .all().values(*selectedCols).annotate(tag=ArrayAgg("tag__id")))
    if item == None or len(item) == 0:
        return JsonResponse({"status": False, "error": "Items doesnt exixst"}, status=404)
    return JsonResponse({
        "status": True,
        "data": item
    })


def getItemsByTag(req, tag_id):
    """
    URI looks like: /found/tag/<tag_id>
    """
    if req.method != "GET":
        return JsonResponse({"status": False, "error": "Method not allowed"}, status=405)
    page_size = req.GET.get("pagesize")
    page_number = req.GET.get("pagenumber")
    if not page_size:
        page_size = 20
    if not page_number:
        page_number = 1
    founditems = Found.objects.filter(ownerFound=False, tag__id__exact=tag_id).order_by(
        "-created").values(*selectedCols).annotate(tag=ArrayAgg("tag__id"))
    paginated = Paginator(list(founditems), page_size)
    curr_page = paginated.get_page(page_number)

    res = {
        "status": True,
        "class": "found",
        "data": curr_page.object_list,
        "page_size": len(curr_page.object_list),
        "has_next_page": curr_page.has_next(),
        "next_page_number": curr_page.next_page_number() if curr_page.number < paginated.num_pages else False,
        "total_pages": paginated.num_pages,
        "total_items": paginated.count,
    }
    return JsonResponse(res)


def searchItem(req):
    if req.method != "GET":
        return JsonResponse({"status": False, "error": "Method not allowed"}, status=405)
    page_size = req.GET.get("pagesize")
    page_number = req.GET.get("pagenumber")
    order = req.GET.get("order")

    if not page_size:
        page_size = 20
    if not page_number:
        page_number = 1
    query = req.GET.get("q")
    tag_id = req.GET.get("tag").split(";")

    if not query and not tag_id:
        return JsonResponse({"status": False, "error": "Invalid Search Query"}, status=400)

    filter = {
        "ownerFound": False,
        "tag__id__in": tag_id,
    }
    if query:
        results = Found.objects.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )
    else:
        results = Found.objects

    if tag_id:
        results = results.filter(tag__id__in=tag_id)

    founditems = results.filter(**filter).order_by(
        "created" if order == "ascending" else "-created").values(*selectedCols).annotate(tag=ArrayAgg("tag__id"))

    paginated = Paginator(list(founditems), page_size)
    curr_page = paginated.get_page(page_number)

    res = {
        "status": True,
        "class": "lost",
        "data": curr_page.object_list,
        "page_size": len(curr_page.object_list),
        "has_next_page": curr_page.has_next(),
        "next_page_number": curr_page.next_page_number() if curr_page.number < paginated.num_pages else False,
        "total_pages": paginated.num_pages,
        "total_items": paginated.count,
    }
    return JsonResponse(res)


__all__ = [
    "latestFound",
    "getItem",
    "newItem",
    "markUserFound",
    "getItemOfUser",
    "getItemsByTag",
    "searchItem",
]
