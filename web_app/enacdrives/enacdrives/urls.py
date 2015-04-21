from django.conf.urls import include, url
from django.contrib import admin

urlpatterns = [
    url(r'^$', 'config.views.http_home'),
    url(r'^get', 'config.views.http_get', name='http_get'),
    url(r'^ldap_settings', 'config.views.http_ldap_settings', name='http_ldap_settings'),
    url(r'^admin/', include(admin.site.urls)),
]
