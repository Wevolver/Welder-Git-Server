from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, JsonResponse

from welder.permissions import decorators as permissions
from welder.analytics import decorators as mixpanel
from welder.notifications import decorators as notification
from welder.git.git import GitResponse
from welder.versions.utilities import fetch_repository
from welder.versions import porcelain
from django.conf import settings


from time import time
from enum import Enum
import logging
import pygit2
import os

logger = logging.getLogger(__name__)

class Actions(Enum):
    advertisement = 'advertisement'
    result = 'result'

@require_http_methods(["GET"])
@mixpanel.track
@permissions.requires_git_permission_to('read')
def info_refs(request, user, project_name, permissions_token=None,  tracking=None):
    """ Initiates a handshake for a smart HTTP connection

    https://git-scm.com/book/en/v2/Git-Internals-Transfer-Protocols

    Args:
        user (string): The user's name.
        project_name (string): The user's repository name.

    Returns:
        GitResponse: A HttpResponse with the proper headers and payload needed by git.
    """

    directory = porcelain.generate_directory(user)
    repo = os.path.join(settings.REPO_DIRECTORY, directory, project_name)
    response = GitResponse(service=request.GET['service'], action=Actions.advertisement.value,
                           repository=repo, data=None)
    return response.get_http_info_refs()

@permissions.requires_git_permission_to('read')
@mixpanel.track
def upload_pack(request, user, project_name, tracking=None):
    """ Calls service_rpc assuming the user is authenticated and has read permissions """

    return service_rpc(user, project_name, request.path_info.split('/')[-1], request.body)

@permissions.requires_git_permission_to('write')
@mixpanel.track
@notification.notify("committed to")
@notification.activity("committed")
def receive_pack(request, user, project_name, permissions_token=None, tracking=None):
    """ Calls service_rpc assuming the user is authenticated and has write permissions """

    return service_rpc(user, project_name, request.path_info.split('/')[-1], request.body)

@mixpanel.track
def service_rpc(user, project_name, request_service, request_body, permissions_token=None, tracking=None):
    """ Calls the Git commands to pull or push data from the server depending on the received service.

    https://git-scm.com/book/en/v2/Git-Internals-Transfer-Protocols

    Args:
        user (string): The user's name.
        project_name (string): The user's repository name.

    Returns:
        GitResponse: An HttpResponse that indicates success or failure and may include the requested packfile
    """

    directory = porcelain.generate_directory(user)
    repo = os.path.join(settings.REPO_DIRECTORY, directory, project_name)
    response = GitResponse(service=request_service, action=Actions.result.value,
                           repository=repo, data=request_body)
    return response.get_http_service_rpc()
