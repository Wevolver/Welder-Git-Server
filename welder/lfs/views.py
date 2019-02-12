from django.views.decorators.http import require_http_methods
from django.http import HttpResponse, JsonResponse
from django.conf import settings

import json
import logging

logger = logging.getLogger(__name__)

import boto3
from botocore.client import Config

"""
Setup boto3 s3 client.
The bucket's region AND the signature version 's3v4' must be specified.
"""
s3_client = boto3.client(
    's3',
    'us-west-1',
    config=Config(signature_version='s3v4'),
    aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
)

def get_s3_url(operation, object_id):
    """ Build Presigned s3 URL"""
    action = 'get_object' if operation == 'download' else 'put_object'
    method = 'GET' if operation == 'download' else 'PUT'

    return s3_client.generate_presigned_url(
        action,
        Params = {
            'Bucket': 'wevolver-lfs',
            'Key': object_id
        },
        ExpiresIn = 18400, # TODO: No reason for this number, what's a good amount?
        HttpMethod = method
    )

def get_lfs_object(operation, object_id, headers, object_size):
    """ Upload or Download the object """
    lfs_object = {
      "oid": object_id,
      "size": object_size,
      "authenticated": True,
      "actions": {
        operation: {
          "href": get_s3_url(operation, object_id),
          "header": headers,
          "expires_in": 18400, # TODO: No reason for this number, what's a good amount?
        }
      }
    }

    return lfs_object

def locks_verify(request, user, project_name, permissions_token=None):
    return JsonResponse({})

def objects_batch(request, user, project_name, permissions_token=None):
    data = json.loads(request.body)
    operation = data.get('operation', None)

    # transfer can only be basic
    transfer = 'basic'
    # List of object to upload/download
    objects = []

    for file_object in data['objects']:
        try:
            object_id = file_object['oid']
            object_size = file_object['size']
            headers = {}
            # https://github.com/git-lfs/git-lfs/blob/master/docs/api/batch.md
            lfs_object = get_lfs_object(operation, object_id, headers, object_size)
        except KeyError:
            lfs_object = None
            print(400)

        if lfs_object:
            objects.append(lfs_object)

    result = {'objects': objects, 'transfer': transfer}

    return JsonResponse(result)

