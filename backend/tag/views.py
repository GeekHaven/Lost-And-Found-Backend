from django.http import JsonResponse
from .models import Tag


def newTag(req):
    if (req.method != "POST"):
        return JsonResponse({"status": False, "error": "Method not allowed"}, status=405)
    id = req.jsonbody(req).get("id")
    name = req.jsonbody(req).get("name")
    img = req.jsonbody(req).get("img")
    if ((not name) and name.length < 33) or ((not id) and id.length < 17):
        return JsonResponse({"status": False, "error": "Invalid Form Data"}, status=400)
    newT = Tag.objects.create(
        id=id,
        name=name,
        img=img,
    )
    return JsonResponse({"status": True, "class": "tag", "data": {"id": newT.id, "name": newT.name}}, status=201)


def getAllTags(req):
    if (req.method != "GET"):
        return JsonResponse({"status": False, "error": "Method not allowed"}, status=405)
    tags = Tag.objects.all().values("id", "name", "img")
    return JsonResponse({"status": True, "class": "tag", "data": list(tags)}, status=200)
