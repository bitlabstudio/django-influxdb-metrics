"""URLs to run the tests."""
from django.contrib import admin

from django import VERSION as DJANGO_VERSION


admin.autodiscover()

if DJANGO_VERSION < (2, 0):
    if DJANGO_VERSION < (1, 4):
        from django.conf.urls.defaults import include, url
    else:
        from django.conf.urls import include, url
    urlpatterns = [
        url(r'^admin/', include(admin.site.urls)),
    ]
else:
    from django.urls import path
    urlpatterns = [
        path('admin/', admin.site.urls),
    ]


