from datetime import datetime
import os
from dotenv import load_dotenv
from django.http import JsonResponse
# from .ldap_auth import getUser
import jwt
import json
from json.decoder import JSONDecodeError
load_dotenv()


tokenHandler = jwt
JWT_SECRET = os.environ.get("JWT_SECRET")


class BasicMiddleware:
    """
    request.auth_user = user || None,
    request.authenticated = True || False,
    request.unauthorisedResponse = Unauthorised User error Response (status code = 401)
    adds a request.auth_user, req.authenticated for making authenticated routes easy
    also adds req.unauthorisedResponse for unauthenticated ROutes error Response
    JWT secret is provided in the HTTP Request Headers under the key "secret"
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.unauthorisedResponse = JsonResponse(
            {"error": "User authentication required"}, status=401)

        def bodytojson(request):
            body_unicode = request.body.decode('utf-8')
            try:
                return json.loads(body_unicode)
            except JSONDecodeError:
                return None
        request.jsonbody = bodytojson
        try:
            secret = request.headers["Authorization"]
        except KeyError:
            secret = None
        if (secret and secret != ""):
            try:
                message = tokenHandler.decode(
                    secret, JWT_SECRET, algorithms="HS256")
                if (datetime.fromisoformat(message["expireon"]) > datetime.now()):
                    request.auth_user = {
                        "uid": message["uid"],
                        "name": message["name"]
                    }
                    request.authenticated = True
                else:
                    request.auth_user = None
                    request.authenticated = False
            except Exception:
                request.auth_user = None
                request.authenticated = False
        else:
            request.auth_user = None
            request.authenticated = False
        response = self.get_response(request)
        return response
