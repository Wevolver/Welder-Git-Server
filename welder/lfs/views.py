from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, JsonResponse
from django.conf import settings

import json
import logging

logger = logging.getLogger(__name__)

import boto3
s3 = boto3.client(
    's3',
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)

def download(c_url, object_id, headers, object_size, object_data):
    """ Download the object """
    return True


def upload(c_url, object_id, headers, object_size, object_data):
    """ Upload the object """
    return True

def locks_verify(request, user, project_name, permissions_token=None,  tracking=None):
    return JsonResponse({})

def objects_batch(request, user, project_name, permissions_token=None,  tracking=None):
    data = json.loads(request.body)
    print(data)
    operation = data.get('operation', None)

    transfer = 'basic'
    url = 'url ' + '/' + 'container'
    objects = []

    handle = download if operation == 'download' else upload

    for file_object in data['objects']:
        try:
            object_id = file_object['oid']
            object_size = file_object['size']
        except KeyError:
            print(400)
            # abort(400)

        object_data = {'oid': object_id}
        href = s3.generate_presigned_url(
            ClientMethod='put_object',
            Params={
                'Bucket': 'wevolver-lfs',
                'Key': object_id
            }
        )
        headers = {'x-auth-token': permissions_token} if permissions_token else {}

        if handle(url, object_id, headers, object_size, object_data):
            action = dict(href=href, header=headers, expires_at=None)
            object_data['actions'] = {operation: action}

        object_data['size'] = object_size
        object_data['authenticated'] = True
        objects.append(object_data)

    result = {'objects': objects, 'transfer': transfer}
    print(result)
    return JsonResponse(result)

