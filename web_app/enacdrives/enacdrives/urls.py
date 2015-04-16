from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^config', 'config.views.http_config', name='http_config'),

    url(r'^admin/', include(admin.site.urls)),
]
