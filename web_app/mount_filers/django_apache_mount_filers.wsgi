# Content of 
# django/apache/mount_filers.wsgi
# or
# django_test/apache/mount_filers.wsgi

import os
import sys
from os.path import dirname,abspath

os.environ['DJANGO_SETTINGS_MODULE'] = 'mount_filers.settings'

# /home/bancal/django or /home/bancal/django_test
my_path = dirname(dirname(abspath(__file__)))
sys.path.append(my_path)

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()

