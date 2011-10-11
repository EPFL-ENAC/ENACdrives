from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('mount_filers.directory',
    url(r'^config', 'views.get_config', name='get_config'),
    url(r'^full_config', 'views.get_full_config'),
    url(r'^domain', 'views.get_domain', name='get_domain'),
    url(r'^sciper', 'views.get_sciper', name='get_sciper'),
    url(r'^labo', 'views.get_labos'),
    url(r'^validate', 'views.validate', name='validate'),
    
    # Example:
    # (r'^mount_filers/', include('mount_filers.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
