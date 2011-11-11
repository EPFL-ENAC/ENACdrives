from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('mount_filers.directory',
    url(r'^config', 'views.http_get_config', name='http_get_config'),
    url(r'^domain', 'views.http_get_domain', name='http_get_domain'),
    url(r'^sciper', 'views.http_get_sciper', name='http_get_sciper'),
    url(r'^labo', 'views.http_get_labos'),
    url(r'^validate', 'views.http_validate', name='http_validate'),
    url(r'^settings', 'views.http_get_settings', name='http_get_settings'),
    
    url(r'^adm/$', 'adm_views.http_adm_browse', name='http_adm_browse'),
    url(r'^adm/edit/(?P<conf_id>\w+)/', 'adm_views.http_adm_edit', name='http_adm_edit'),
    
    url(r'^adm_config_dump/', 'adm_views.http_get_config_dump'),
    
    # Example:
    # (r'^mount_filers/', include('mount_filers.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
)
