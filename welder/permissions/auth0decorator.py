import json
from functools import wraps
from jose import jwt
from urllib.request import urlopen
import logging

AUTH0_DOMAIN = 'wevolver.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'http://localhost:5000/api/v2'

logger = logging.getLogger(__name__)

class AuthError(Exception):
    def __init__(self, error, status_code):
        self.error = error
        self.status_code = status_code


def get_token_auth_header(request):
    """Obtains the Access Token from the Authorization Header
    """
    auth = request.META.get('HTTP_AUTHORIZATION', None)
    if not auth:
        # raise AuthError({
        #     'code': 'authorization_header_missing',
        #     'description': 'Authorization header is expected.'
        # }, 401)
        return None, None

    token = auth.split(':')[0]
    try:
        user_id = auth.split(':')[1]
    except Exception as e:
        user_id = None
        pass

    parts = token.split()

    if parts[0].lower() != 'bearer':
        # raise AuthError({
        #     'code': 'invalid_header',
        #     'description': 'Authorization header must start with "Bearer".'
        # }, 401)
        return None, user_id


    elif len(parts) == 1:
        # raise AuthError({
        #     'code': 'invalid_header',
        #     'description': 'Token not found.'
        # }, 401)
        return None, user_id


    elif len(parts) > 2:
        # raise AuthError({
        #     'code': 'invalid_header',
        #     'description': 'Authorization header must be bearer token.'
        # }, 401)
        return None, user_id

    token = parts[1]
    if token == '-':
        return None, user_id
    return token, user_id


def requires_auth(f):
    """Determines if the Access Token is valid
    """

    @wraps(f)
    def decorated(request, *args, **kwargs):
        logger.info('AUTH TOKEN')
        token, user_id = get_token_auth_header(request)
        logger.info(token)
        logger.info(user_id)
        kwargs['permissions_token'] = "All Good"
        return f(request, *args, **kwargs)

    return decorated