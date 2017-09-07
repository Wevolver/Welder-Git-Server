from django.conf import settings
from mixpanel import Mixpanel
from functools import wraps
import logging

mixpanel = Mixpanel(settings.TRACKING_TOKEN)
logger = logging.getLogger(__name__)

name_mapping = {
    # 'create_project': "Created Project",
    # 'delete_project': "Deleted Project",
    # 'read_file': "Read File",
    # 'read_history': "Read History",
    # 'create_new_folder': "Created Folder",
    # 'receive_files': "Uploaded Files",
    # 'list_bom': "Read Bom",
    # 'download_archive': "Downloaded Archive",
    # 'info_refs': "Git Info",
    # 'read_tree': "Read Tree",
    'upload_pack': "Git Read",
    'receive_pack': "Git Write"
}

def track(func):
    @wraps(func)
    def _decorator(request, *args, **kwargs):
        # if settings.DEBUG:
        #     return func(request, *args, **kwargs)
        title = name_mapping.get(func.__name__, False)
        if title:
            print(func)
            print(args)
            print(kwargs)
            user = kwargs['user']
            project = kwargs['project_name']
            mixpanel.track(user, title, {
               'project': project,
               'function': func.__name__
            })
        return func(request, *args, **kwargs)
    return _decorator
