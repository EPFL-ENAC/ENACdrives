# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('releases', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='installer',
            old_name='file_path',
            new_name='storage_name',
        ),
    ]
