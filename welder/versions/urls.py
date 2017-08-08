from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^(?P<user>[-.\w]+)/(?P<project_name>[-.\w\s]+)/create$', views.create_project, name='create-project'),
    url(r'^(?P<user>[-.\w]+)/(?P<project_name>[-.\w\s]+)/delete$', views.delete_project, name='delete-project'),
    url(r'^(?P<user>[-.\w]+)/(?P<project_name>[-.\w\s]+)/readfile$', views.read_file, name='read-file'),
    url(r'^(?P<user>[-.\w]+)/(?P<project_name>[-.\w\s]+)/readhistory$', views.read_history, name='read-history'),
    url(r'^(?P<user>[-.\w]+)/(?P<project_name>[-.\w\s]+)/newfolder$', views.create_new_folder, name='new-folder'),
    url(r'^(?P<user>[-.\w]+)/(?P<project_name>[-.\w\s]+)/upload$', views.receive_files, name='receive-files'),
    url(r'^(?P<user>[-.\w]+)/(?P<project_name>[-.\w\s]+)/listbom$', views.list_bom, name='list-bom'),
    url(r'^(?P<user>[-.\w]+)/(?P<project_name>[-.\w\s]+)/archive/download$', views.download_archive, name='download-archive'),
    url(r'^(?P<user>[-.\w]+)/(?P<project_name>[-.\w\s]+)/git-upload-pack$', views.upload_pack, name='upload_pack'),
    url(r'^(?P<user>[-.\w]+)/(?P<project_name>[-.\w\s]+)/git-receive-pack$', views.receive_pack, name='receive_pack'),
    url(r'^(?P<user>[-.\w]+)/(?P<project_name>[-.\w\s]+)/info/refs$', views.info_refs, name='info-refs'),
    url(r'^(?P<user>[-.\w]+)/(?P<project_name>[-.\w\s]+)$', views.read_tree, name='read-tree'),
]
