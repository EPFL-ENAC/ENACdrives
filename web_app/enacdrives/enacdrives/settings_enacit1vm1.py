# Settings specific to enacit1sbtest4.epfl.ch

ADMINS = (('Samuel Bancal', 'Samuel.Bancal@epfl.ch'),)
EMAIL_HOST = "mail.epfl.ch"
EMAIL_SUBJECT_PREFIX = "[ENACdrives on enacit1vm1] "
SERVER_EMAIL = "no-reply@enacit1vm1.epfl.ch"

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '=-xh#cssh$h6^g)tvak#w(w9s95apy2p76r1xag4tnk#-n=br!'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ["enacit1vm1", "enacit1vm1.epfl.ch", "enacdrives", "enacdrives.epfl.ch"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'HOST': '',
        'NAME': 'enacdrives',
        'USER': 'enacdrives',
        'PASSWORD': 'gV#aN,LX5-',
    }
}

APACHE_PRIVATE_DIR = "/data/local/enacdrives/installers"
FILE_UPLOAD_TEMP_DIR = "/data/local/enacdrives/uploads"

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
