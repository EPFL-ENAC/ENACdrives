from django.conf.urls import url

urlpatterns = [
    url(r"^$", "releases.views.http_home"),
    url(r"^admin/?$", "releases.views.http_admin", name="http_admin"),
    url(r"^upload$", "releases.views.do_upload", name="do_upload"),
    url(r"^enable$", "releases.views.do_enable", name="do_enable"),
    url(r"^download$", "releases.views.do_download", name="do_download"),
    url(
        r"^api/latest_release_number$",
        "releases.views.api_latest_release_number",
        name="api_latest_release_number",
    ),
    url(
        r"^api/latest_release_date$",
        "releases.views.api_latest_release_date",
        name="api_latest_release_date",
    ),
]
