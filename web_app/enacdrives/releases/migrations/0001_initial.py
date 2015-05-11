# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Installer',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, verbose_name='ID', auto_created=True)),
                ('upload_username', models.CharField(max_length=256)),
                ('upload_date', models.DateTimeField()),
                ('release_number', models.CharField(max_length=256)),
                ('os', models.CharField(default='a', choices=[('a', 'Windows'), ('b', 'Linux'), ('c', 'MacOSX')], max_length=1)),
                ('file_name', models.CharField(max_length=256)),
                ('file_path', models.CharField(max_length=256)),
                ('enabled', models.BooleanField(default=False)),
            ],
        ),
    ]
