from django.core.exceptions import PermissionDenied
from django.http import HttpResponse, JsonResponse
from django.http import HttpResponseForbidden
from django.conf import settings
from profilehooks import profile
from time import gmtime, strftime
from functools import wraps
import requests
import logging
import base64
import json
import jwt
import os

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG)
def requires_permission_to(permission):
    """ Determines the user and authorization through Wevolver token based auth

    Uses the request's access_token and user_id params to check the user's bearer
    token against the Wevolver API

    Calls the project permission endpoint with the current user's id to
    get a list of permissions based on their role
    """
    def has_permission(func):
        @wraps(func)
        def _decorator(request, *args, **kwargs):
            action = request.GET.get("action", None)
            if settings.DEBUG or action == 'create':
                kwargs['permissions_token'] = "All Good"
                return func(request, *args, **kwargs)

            access_token = request.META.get('HTTP_AUTHORIZATION', None)
            access_token = access_token if access_token else request.GET.get("access_token")

            permissions = request.META.get('HTTP_PERMISSIONS', None)
            permissions = permissions if permissions else request.GET.get("permissions")

            project_name = kwargs['project_name']
            user_id = request.GET.get("user_id")

            user_name = kwargs['user']

            host_url = "{}/permissions".format(settings.API_V2_BASE)
            if 'is_welder' in str(request.POST):
                host_url =  "https://api.wevolver.com/welder/api/v2/permissions"

            if not permissions:
                success, response = get_token(user_name, project_name, access_token, url=host_url)
                decoded_token = {  "project": "default", "permissions": "['read']"}
                token = 'default'
                if success:
                    token = response.content
                    decoded_token = decode_token(token)
                permissions = decoded_token['permissions'] if decoded_token else ''

            else:
                token = permissions
                decoded_token = decode_token(token)
                right_project = decoded_token['project'] == project_name if decoded_token else None
                not_permissions = not decoded_token or not right_project
                if not_permissions:
                    success, response = get_token(user_name, project_name, access_token, url=host_url)
                    token = response.content
                    decoded_token = decode_token(token)
                    try:
                        permissions = decoded_token['permissions']
                    except:
                        permissions = ['none']

                elif not permissions:
                    permissions = ['none']
                else:
                    permissions = decoded_token['permissions']

            if decoded_token and (decoded_token['project'] == project_name or decoded_token['project']=='default') and permission in permissions:
                kwargs['permissions_token'] = token
                return func(request, *args, **kwargs)
            elif permissions and permission == 'create' and permission in permissions:
                kwargs['permissions_token'] = token
                return func(request, *args, **kwargs)
            else:
                return HttpResponseForbidden('No Permissions')
        return _decorator
    return has_permission

def requires_git_permission_to(permission):
    """ Determines the user and authorization through basic http auth

    Uses the requests HTTP_AUTHORIZATION to authorize the user against
    basic HTTP auth
    """
    def has_git_permission(func):
        @wraps(func)
        def _decorator(request, *args, **kwargs):
            if settings.DEBUG:
                return func(request, *args, **kwargs)

            user_name = kwargs['user']
            project_name = kwargs['project_name']
            access_token = None
            user_id = None

            if request.META.get('HTTP_AUTHORIZATION'):
                access_token, user_id = basic_auth(request.META['HTTP_AUTHORIZATION'])

            success, response = get_token(user_name, project_name, access_token, url="https://api.wevolver.com/welder/api/v2/permissions")
            # success, response = get_token(user_name, project_name, user_id, url="http://localhost:5000/api/v2/permissions")
            token = 'default'
            if success:
                token = response.content
                decoded_token = decode_token(token)
            else:
                decoded_token = False
            permissions = decoded_token['permissions'] if decoded_token else ''
            if permissions and permission in permissions:
                return func(request, *args, **kwargs)

            res = HttpResponse()
            res.status_code = 401
            res['WWW-Authenticate'] = 'Basic'
            print(res)
            return res
        return _decorator
    return has_git_permission

def basic_auth(authorization_header):
    """ Basic auth middleware for git requests

    Attempts to log the current user into the Wevolver API login endpoint

    Args:
        authorization_header (str): the current user's bearer token
    """
    authorization_method, authorization = authorization_header.split(' ', 1)
    if authorization_method.lower() == 'basic':
        authorization = base64.b64decode(authorization.strip()).decode('utf8')
        username, password = authorization.split(':', 1)
        username = username
        password = password
        body = {'username': str(username),
                'password': str(password),
                'client_id': "r8PPxUDuHwCOSPy51Qg3PgNmLFCulUHO",
                'grant_type': 'password'}
        url = "https://welder.eu.auth0.com/oauth/token"
        response = requests.post(url, data=body)
        try:
            response = (json.loads(response.content)['access_token'], json.loads(response.content)['id_token'])
            return response
        except:
            res = HttpResponse()
            res.status_code = 401
            res['WWW-Authenticate'] = 'Basic'
            return (None, res)
    else:
        return (None, 'Default')

def get_token(user_name, project_name, access_token, user_id=None, url="{}/permissions".format(settings.API_V2_BASE)):
    """ Checks against the Wevolver API to see if the users token is currently valid

    Args:
        authorization (str): the current user's bearer token
        user (str): the current requesting user's id
    """
    body = json.dumps({
        'project': "{}/{}".format(user_name, project_name),
        'user_id': user_id
    })

    if access_token:
        headers = {
            'Authorization': '{}'.format(access_token),
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
        }
    else:
        headers = {
            'Accept': 'application/json, text/plain, */*',
            'Content-Type': 'application/json',
        }
    try:
        response = requests.post(url, headers=headers, data=body)
        return (response.status_code == requests.codes.ok, response)
    except Exception as e:
        logger.info(e)
        return(False, {'content': False})

def decode_token(token):
    """ Decodes the received token using Wevolvers JWT public key

    Args:
        token (str): the received token
        user_id (str): the current requesting user's id
        user_name (str): the current requesting user
        user_name (str): the current requesting user's project
    """
    try:
        with open('./welder/permissions/jwt.verify','r') as verify:
            try:
                return jwt.decode(token, verify.read(), algorithms=['RS256'], issuer='wevolver')
            except jwt.ExpiredSignatureError as error:
                print(error)
                return None
    except Exception as e:
        print(e)
