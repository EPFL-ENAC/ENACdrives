from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^$', 'config.views.http_home'),
    url(r'^get', 'config.views.http_get', name='http_get'),
    url(r'^admin/', include(admin.site.urls)),
]
