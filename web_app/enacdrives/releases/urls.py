from django.conf.urls import url

urlpatterns = [
    url(r"^$", "releases.views.http_download"),
    url(r"^admin/?$", "releases.views.http_admin", name="http_admin"),
    url(r"^download/?$", "releases.views.http_download", name="http_download"),
    url(r"^upload$", "releases.views.http_upload", name="http_upload"),
    url(r"^api/latest_release_number$", "releases.views.api_latest_release_number", name="api_latest_release_number")
]
