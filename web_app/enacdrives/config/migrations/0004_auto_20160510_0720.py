# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("config", "0003_auto_20150619_1309"),
    ]

    operations = [
        migrations.AddField(
            model_name="config",
            name="client_filter_os",
            field=models.CharField(max_length=256, blank=True, default=""),
        ),
        migrations.AddField(
            model_name="config",
            name="client_filter_os_version",
            field=models.CharField(max_length=256, blank=True, default=""),
        ),
        migrations.AddField(
            model_name="config",
            name="client_filter_version",
            field=models.CharField(max_length=256, blank=True, default=""),
        ),
    ]
