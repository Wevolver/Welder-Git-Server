from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, JsonResponse
import json
import logging

logger = logging.getLogger(__name__)


def locks_verify(request, user, project_name, permissions_token=None,  tracking=None):
    return JsonResponse({'msg': 'response.text'})

def objects_batch(request, user, project_name, permissions_token=None,  tracking=None):
    post = json.loads(request.body)
    print(post.get('operation', None))
    return JsonResponse({'msg': 'response.text'})

