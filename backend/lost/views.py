from django.db.models import Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from django import forms
from django.contrib.postgres.aggregates import ArrayAgg

from .models import Lost
from tag.models import Tag


class NewItemForm(forms.Form):
    title = forms.CharField(max_length=50, strip=True)
    description = forms.CharField(max_length=300, strip=True, required=False)
    location = forms.CharField(max_length=100, required=False, strip=True)
    lostDate = forms.DateTimeField(required=False)
    contactEmail = forms.EmailField(required=False)
    contactPhone = forms.CharField(max_length=10)
    image = forms.URLField(max_length=300, required=False)
    tagIds = forms.CharField(max_length=300, required=False, strip=True)


selectedCols = [
    "id",
    "user_id",
    "user_name",
    "title",
    "description",
    "created",
    "location",
    "lostDate",
    "contactPhone",
    "contactEmail",
    "image",
    "found",
]


def latestLost(req):
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

    lostitemsquery = Lost.objects.filter(found=False)

    if query:
        lostitemsquery = lostitemsquery.filter(Q(title__icontains=query) | Q(
            description__icontains=query) | Q(location__icontains=query))

    if tag_id:
        tag_id = tag_id.split(";")
        lostitemsquery = lostitemsquery.filter(tag__id__in=tag_id)

    lostitems = lostitemsquery.order_by(
        "created" if order == "ascending" else "-created").values(*selectedCols).annotate(tag=ArrayAgg("tag__id"))

    paginated = Paginator(lostitems, page_size)
    curr_page = paginated.get_page(page_number)

    res = {
        "status": True,
        "class": "lost",
        # "data": list(map(lambda lostitem: models.model_to_dict(lostitem).update({"tags": lostitem.tag.all()}), curr_page.object_list)),
        "data": list(curr_page.object_list),
        "page_size": len(curr_page.object_list),
        "has_next_page": curr_page.has_next(),
        "next_page_number": curr_page.next_page_number() if curr_page.number < paginated.num_pages else False,
        "total_pages": paginated.num_pages,
        "total_items": paginated.count,
    }

    return JsonResponse(res)


def getItem(req, id):
    """
    URI looks like: /lost/<id>
    """
    if req.method != "GET":
        return JsonResponse({"status": False, "error": "Method not allowed"}, status=405)

    item = Lost.objects.filter(id__exact=id).values(
        *selectedCols).annotate(tag=ArrayAgg("tag__id")).first()
    if item == None:
        return JsonResponse({"status": False, "error": "Item not found"}, status=404)
    return JsonResponse({
        "status": True,
        "class": "lost",
        "data": item
    })


def newItem(req):
    if not req.authenticated:
        return req.unauthorisedResponse

    if req.method != "POST":
        return JsonResponse({"status": False, "error": "Method not allowed"}, status=405)
    form = NewItemForm(req.jsonbody(req))
    if form.is_valid():
        newLost = Lost.objects.create(
            user_id=req.auth_user["uid"],
            user_name=req.auth_user["name"],
            title=form.cleaned_data["title"],
            description=form.cleaned_data["description"],
            location=form.cleaned_data["location"],
            lostDate=form.cleaned_data["lostDate"],
            contactEmail=form.cleaned_data["contactEmail"],
            contactPhone=form.cleaned_data["contactPhone"],
            image=form.cleaned_data["image"],
        )
        tagsIdArray = form.cleaned_data["tagIds"].split(";")
        tags = Tag.objects.filter(id__in=tagsIdArray).all() or []
        newLost.tag.set(list(tags))
        return JsonResponse({
            "status": True,
            "class": "lost",
            "data": {
                "itemId": newLost.id
            }
        }, status=201)
    return JsonResponse({"status": False, "error": "Invalid Form Data"}, status=400)


def markFound(req):
    if not req.authenticated:
        return req.unauthorisedResponse
    if req.method != "POST":
        return JsonResponse({"status": False, "error": "Method not allowed"}, status=405)

    lostitem = Lost.objects.filter(id=req.jsonbody(req).get(
        "id"), user_id=req.auth_user["uid"]).first()
    if not lostitem:
        return JsonResponse({"status": False, "error": "Item not found"}, status=404)

    lostitem.found = True
    lostitem.save()

    return JsonResponse({
        "status": True
    })

# to get all item from a user


def getItemOfUser(req, user_id):
    """
    URI looks like: /lost/user/<user_id>
    """
    if req.method != "GET":
        return JsonResponse({"status": False, "error": "Method not allowed"}, status=405)
    item = list(Lost.objects.filter(
        user_id__iexact=user_id) .all().order_by("-created").values(*selectedCols).annotate(tag=ArrayAgg("tag__id")))
    if item == None or len(item) == 0:
        return JsonResponse({"status": False, "error": "Items doesnt exist"}, status=404)
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
    lostitems = Lost.objects.filter(found=False, tag__id__exact=tag_id).order_by(
        "-created").values(*selectedCols).annotate(tag=ArrayAgg("tag__id"))
    paginated = Paginator(list(lostitems), page_size)
    curr_page = paginated.get_page(page_number)

    res = {
        "status": True,
        "class": "lost",
        "data": list(curr_page.object_list),
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
    if not page_size:
        page_size = 20
    if not page_number:
        page_number = 1
    query = req.GET.get("q")
    if not query:
        return JsonResponse({"status": False, "error": "Invalid Search Query"}, status=400)
    results = Lost.objects.filter(
        Q(title__icontains=query) | Q(description__icontains=query)
    ).order_by("-created").values(*selectedCols).annotate(tag=ArrayAgg("tag__id"))
    paginated = Paginator(list(results), page_size)
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
    "latestLost",
    "getItem",
    "newItem",
    "markFound",
    "getItemOfUser",
    "searchItem",
    "getItemsByTag"
]
