# Bancal Samuel
# 111107

import os

ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

EMAIL_HOST = "mail.epfl.ch"
EMAIL_SUBJECT_PREFIX = "[mount_filers - Django app - DEV] "

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': os.path.join(ROOT_PATH, 'db/mount_filers_db_dev.sqlite'),
    }
}


SECRET_KEY = '$+(kw7@!_1&1&xn_nupq(3n8zj-sg_)8h_wkb3$!f7omllrq41'
