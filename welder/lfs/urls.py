from django.conf.urls import url
from welder.lfs import views

urlpatterns = [
    url(r'^(?P<user>[-.\w]+)/(?P<project_name>[-.\w\s]+)/info/lfs/locks/verify$', views.locks_verify, name='locks_verify'),
    url(r'^(?P<user>[-.\w]+)/(?P<project_name>[-.\w\s]+)/info/lfs/objects/batch$', views.objects_batch, name='objects_batch'),
]
