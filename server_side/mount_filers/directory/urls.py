from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('mount_filers.directory',
    (r'^config', 'views.get_config'),
    (r'^domain', 'views.get_domains'),
    (r'^sciper', 'views.get_sciper'),
    (r'^labo', 'views.get_labos'),
    
    # Example:
    # (r'^mount_filers/', include('mount_filers.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
