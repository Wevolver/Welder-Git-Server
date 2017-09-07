from django.conf import settings
from mixpanel import Mixpanel
from functools import wraps
import logging

mixpanel = Mixpanel(settings.TRACKING_TOKEN)
logger = logging.getLogger(__name__)

def track(func):
    @wraps(func)
    def _decorator(request, *args, **kwargs):
        # if settings.DEBUG:
        #     return func(request, *args, **kwargs)
        user = kwargs['user']
        project = kwargs['project_name']
        mixpanel.track(user, func.__name__, {
           'project': project
        })
        return func(request, *args, **kwargs)
    return _decorator
