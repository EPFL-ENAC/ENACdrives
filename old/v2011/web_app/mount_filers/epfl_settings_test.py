# Bancal Samuel
# 111107

EMAIL_HOST = "mail.epfl.ch"
EMAIL_SUBJECT_PREFIX = "[mount_filers - Django app - TEST] "

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mount_filers_tst',
        'USER': 'mount_filers_tst',
        'PASSWORD': 'Bertat0Z',
        'HOST': '',
        'PORT': '',
    }
}


SECRET_KEY = '$+(kw7@!_1&1&xn_nupq(3n8zj-sg_)8h_wkb3$!f7omllrq41'
