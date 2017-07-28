from django.views.decorators.http import require_http_methods
from django.http import HttpResponse
from django.conf import settings
import requests
import logging
import json

logger = logging.getLogger(__name__)

@require_http_methods(["POST"])
def login(request):
    """ Requests a client_token from the Wevolver Auth application

    Using the requesting user's username and password, we send a authorization
    request to the login endpoint Wevolver's authenication/authorization (/o) API.

    Returns:
        HttpResponse: An object containing all session metadata
    """
    post = json.loads(request.body)
    body = {'username': post['username'], 'password': post['password'], 'grant_type': 'password'}
    url = "{}/proxy-client-token".format(settings.AUTH_BASE)
    response = requests.post(url, data=body)
    return HttpResponse(response.text)
