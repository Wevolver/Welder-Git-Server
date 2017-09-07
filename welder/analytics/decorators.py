from django.conf import settings
from mixpanel import Mixpanel
from functools import wraps
import logging

mixpanel = Mixpanel(settings.TRACKING_TOKEN)
logger = logging.getLogger(__name__)

def track():
    def has_permission(func):
        @wraps(func)
        def _decorator(request, *args, **kwargs):
            # if settings.DEBUG:
            #     return func(request, *args, **kwargs)
            user_name = kwargs['user']
            mp.track(user_name, 'Tracked via decorator', {
                'Test1': 'test'
            })
            return func(request, *args, **kwargs)
        return _decorator
    return has_permission
