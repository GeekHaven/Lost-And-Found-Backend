# For LDAP auth
# from .ldap_auth import auth

# for Aviral auth
from .aviral_auth import auth

from .exceptions import InvalidPassword, ServerError, InvalidUser
from django import forms
from django.http import JsonResponse

from django.conf import settings

from PIL import Image
import os
from secrets import token_urlsafe
import pathlib
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv
load_dotenv()



class AuthForm(forms.Form):
    username = forms.CharField(max_length=20)
    password = forms.CharField(max_length=30)


"""
JWT message structure: {
    "uid"   :   "Roll No.",
    "name"  :   "Name",
    "exp"   :   "Expiry Time" // 1 month from creation
}
"""
tokenHandler = jwt
JWT_SECRET = os.environ.get("JWT_SECRET")

def imageUpload(req):
    if not (req.authenticated):
        return req.unauthorisedResponse
    if (req.method == 'POST'):
        img_file = req.FILES.get('image', None)
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
                return JsonResponse({
                    "status": True,
                    "url": file_url
                }, status=201)
        return JsonResponse({
            "status": False,
            "error": "Invalid Image"
        }, status=400)
    return JsonResponse({"status": False, "error": "Method not allowed"}, status=405)


def authUser(req):
    """
    Authenticated User's LDAP credentials and provides JWT secret in response
    """
    if req.method == "POST":
        form = AuthForm(req.jsonbody(req))
        if form.is_valid():
            try:
                authorised_acc = auth(
                    form.cleaned_data["username"].strip(), form.cleaned_data["password"])
            except InvalidPassword:
                return JsonResponse({"status": False, "error": "Wrong Password"}, status=401)
            except InvalidUser:
                return JsonResponse({"status": False, "error": "Invalid Username"}, status=401)
            except ServerError as e:
                return JsonResponse({"status": False, "error": e.message}, status=500)

            msg = {
                "uid":   authorised_acc["uid"],
                "name":   authorised_acc["name"],
                "expireon":   str(datetime.now() + timedelta(days=30))
            }
            jwt_token = tokenHandler.encode(msg, JWT_SECRET, algorithm="HS256")

            return JsonResponse({
                "status": True,
                "secret": jwt_token
            }, status=200)
        return JsonResponse({"status": False, "error": "Invalid Form Data"}, status=400)
    return JsonResponse({"status": False, "error": "Method not allowed"}, status=405)


def getSelfUser(req):
    if not req.authenticated:
        return req.unauthorisedResponse
    if req.method == "GET":
        return JsonResponse({
            "status": True,
            "username": req.auth_user["uid"],
            "name": req.auth_user["name"]
        }, status=200)
    return JsonResponse({"status": False, "error": "Method not allowed"}, status=405)
