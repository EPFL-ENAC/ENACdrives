from django.conf.urls import url

urlpatterns = [
    url(
        r"^validate_username$",
        "config.views.http_validate_username",
        name="http_validate_username",
    ),
    url(r"^get$", "config.views.http_get", name="http_get"),
    url(
        r"^ldap_settings$", "config.views.http_ldap_settings", name="http_ldap_settings"
    ),
]
