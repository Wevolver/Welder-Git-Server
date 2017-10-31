from welder.versions import porcelain
from welder.permissions.decorators import basic_auth

from django.conf import settings
from functools import wraps

import requests
import logging
import pygit2
import json
import os

logger = logging.getLogger(__name__)

def notify(action):
    def notification(func):
        @wraps(func)
        def _decorator(request, *args, **kwargs):
            if settings.DEBUG:
                return func(request, *args, **kwargs)

            project_name = kwargs['project_name']
            user_name = kwargs['user']

            directory = porcelain.generate_directory(user_name)
            repo = pygit2.Repository(os.path.join(settings.REPO_DIRECTORY, directory, project_name))
            walker = repo.walk(repo.head.target, pygit2.GIT_SORT_TIME)

            existing_commits = []
            for i in range(5):
                existing_commits.append(next(walker).tree_id)

            to_return = func(request, *args, **kwargs)
            access_token = request.META.get('HTTP_AUTHORIZATION', None)
            access_token = access_token if access_token else request.GET.get("access_token")

            try:
                basic, user = basic_auth(access_token)
                access_token = basic if basic else access_token
            except:
                logger.info('not basic auth')

            permissions = request.META.get('HTTP_PERMISSIONS', None)
            permissions = permissions if permissions else request.GET.get("permissions")
            user_id = request.GET.get("user_id")

            events = []
            walker = repo.walk(repo.head.target, pygit2.GIT_SORT_TIME)
            for i in range(5):
                commit = next(walker)
                if commit.tree_id not in existing_commits:
                    events.append({
                      "who": commit.committer.email,
                      "what": commit.message,
                      "where": repo.head.name.split('/')[-1]
                    })

            if(access_token):
                send_notification(user_name, project_name, action, access_token, events)

            kwargs['permissions_token'] = 'required'

            return to_return
        return _decorator
    return notification


def send_notification(user_name, project_name, verb, access_token, events):
    body = {
        'verb': verb,
        'event': json.dumps(events),
        'project': "{}/{}".format(user_name, project_name)
    }

    url = "{}/notify/".format(settings.API_BASE)
    access_token = access_token if access_token.split()[0] == "Bearer" else 'Bearer {}'.format(access_token)
    headers = {'Authorization': '{}'.format(access_token)}
    response = requests.post(url, headers=headers, data=body)

    return (response.status_code == requests.codes.ok, response)
