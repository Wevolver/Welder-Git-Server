from django.conf.urls import url
from welder.git import views

urlpatterns = [
    url(r'^(?P<user>[-.\w]+)/(?P<project_name>[-.\w\s]+)/git-upload-pack$', views.upload_pack, name='upload_pack'),
    url(r'^(?P<user>[-.\w]+)/(?P<project_name>[-.\w\s]+)/git-receive-pack$', views.receive_pack, name='receive_pack'),
    url(r'^(?P<user>[-.\w]+)/(?P<project_name>[-.\w\s]+)/info/refs$', views.info_refs, name='info-refs'),
]
