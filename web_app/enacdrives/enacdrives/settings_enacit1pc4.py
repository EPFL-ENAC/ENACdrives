# Settings specific to enacit1pc4.epfl.ch

import os

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '=-s95apy2p(w9tnk#-n=h76r1xag4x^g)tvak#w#cssh$h6br!'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["enacit1pc4", "enacit1pc4.epfl.ch", "salsa", "salsa.epfl.ch"]

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
    }
}
