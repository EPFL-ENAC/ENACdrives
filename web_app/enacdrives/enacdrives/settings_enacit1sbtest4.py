# Settings specific to enacit1sbtest4.epfl.ch

ADMINS = (('Samuel Bancal', 'Samuel.Bancal@epfl.ch'),)
EMAIL_HOST = "mail.epfl.ch"
EMAIL_SUBJECT_PREFIX = "[ENACdrives on enacit1sbtest4] "
SERVER_EMAIL = "no-reply@enacit1sbtest4.epfl.ch"

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '=-s95apy2p(w9tnk#-n=h76r1xag4x^g)tvak#w#cssh$h6br!'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["enacit1sbtest4", "enacit1sbtest4.epfl.ch", "enacdrives", "enacdrives.epfl.ch"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '',
        'NAME': 'enacdrives',
        'USER': 'enacdrives',
        'PASSWORD': 'h76r1xag',
    }
}

APACHE_PRIVATE_DIR = "/var/www/enacdrives.epfl.ch/private"
FILE_UPLOAD_TEMP_DIR = "/var/www/enacdrives.epfl.ch/upload"

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'debug': {
            'level': 'DEBUG',
            'class': 'logging.FileHandler',
            'filename': '/var/log/django-enacdrives/debug.log',
        },
    },
    'loggers': {
        'django.request': {
            'handlers': ['debug'],
            'level': 'DEBUG',
            'propagate': True,
        },
        'debug': {
            'handlers': ['debug'],
            'level': 'DEBUG',
            'propagate': True,
        },
    },
}
