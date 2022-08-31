# Settings specific to enacit1pc4.epfl.ch

import os

ADMINS = (("Samuel Bancal", "Samuel.Bancal@epfl.ch"),)
EMAIL_HOST = "mail.epfl.ch"
EMAIL_SUBJECT_PREFIX = "[ENACdrives on enacit1pc4] "
SERVER_EMAIL = "no-reply@enacit1pc4.epfl.ch"

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = "=-s95apy2p(w9tnk#-n=h76r1xag4x^g)tvak#w#cssh$h6br!"

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    "enacit1pc4",
    "enacit1pc4.epfl.ch",
    "salsa",
    "salsa.epfl.ch",
    "128.178.7.66",
]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
    }
}

APACHE_PRIVATE_DIR = "/var/www/enacdrives.epfl.ch/private"
FILE_UPLOAD_TEMP_DIR = "/var/www/enacdrives.epfl.ch/upload"
STATIC_ROOT = "/var/www/enacdrives.epfl.ch/static"

# LOGGING = {
#     'version': 1,
#     'disable_existing_loggers': False,
#     'handlers': {
#         'file': {
#             'level': 'DEBUG',
#             'class': 'logging.FileHandler',
#             'filename': '/var/log/apache/django/debug.log',
#         },
#     },
#     'loggers': {
#         'django.request': {
#             'handlers': ['file'],
#             'level': 'DEBUG',
#             'propagate': True,
#         },
#     },
# }
