import requests
import logging

logger = logging.getLogger(__name__)


from django.conf import settings
from functools import wraps

def notify(action):
    def notification(func):
        @wraps(func)
        def _decorator(request, *args, **kwargs):
            if settings.DEBUG:
                return func(request, *args, **kwargs)

            access_token = request.META.get('HTTP_AUTHORIZATION', None)
            access_token = access_token if access_token else request.GET.get("access_token")

            permissions = request.META.get('HTTP_PERMISSIONS', None)
            permissions = permissions if permissions else request.GET.get("permissions")
            user_id = request.GET.get("user_id")

            project_name = kwargs['project_name']
            user_name = kwargs['user']

           email = request.POST.get('email', 'git@wevolver.com')
           message = request.POST.get('commit_message', 'received new files')
           branch = request.GET.get('branch', 'master')
           event = {
             "who": email,
             "what": message,
             "where": branch
           }

           logger.info(event)

            if(access_token):
                send_notifiation(user_name, project_name, action, access_token)

            kwargs['permissions_token'] = 'required'
            return func(request, *args, **kwargs)
        return _decorator
    return notification


def send_notification(user_name, project_name, verb, access_token):
    body = {
        'verb': verb,
        'project': "{}/{}".format(user_name, project_name)
    }

    url = "{}/notify/".format(settings.API_BASE)
    access_token = access_token if access_token.split()[0] == "Bearer" else 'Bearer {}'.format(access_token)
    print(access_token)
    headers = {'Authorization': '{}'.format(access_token)}
    response = requests.post(url, headers=headers, data=body)

    return (response.status_code == requests.codes.ok, response)
