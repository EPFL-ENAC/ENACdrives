from django.conf.urls import include, url
from django.contrib import admin


urlpatterns = [
    url(r"^$", "releases.views.http_download"),
    url(r"^admin/", include(admin.site.urls)),
    url(r"^config/", include("config.urls")),
    url(r"^releases/", include("releases.urls")),
]
