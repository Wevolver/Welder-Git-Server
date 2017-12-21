from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^admin/', admin.site.urls),
    url(r'^', include('welder.permissions.urls')),
    url(r'^', include('welder.versions.urls')),
    url(r'^', include('welder.git.urls')),
    url(r'^', include('welder.lfs.urls')),
]
