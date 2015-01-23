from mount_filers.directory.models import Config, ConfigAdmin, Username, Groupname
from django.contrib import admin

admin.site.register(Config, ConfigAdmin)
