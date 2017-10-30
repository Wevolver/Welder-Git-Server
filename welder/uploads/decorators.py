from welder.versions.uploadhandlers import DirectoryUploadHandler
from welder.versions.uploadhandlers import DirectoryUploadHandlerBig
from django.conf import settings
from functools import wraps

def add_handlers(func):
    @wraps(func)
    def _decorator(request, *args, **kwargs):
        request.upload_handlers.insert(0, DirectoryUploadHandler())
        request.upload_handlers.insert(0, DirectoryUploadHandlerBig())
        return func(request, *args, **kwargs)
    return _decorator
