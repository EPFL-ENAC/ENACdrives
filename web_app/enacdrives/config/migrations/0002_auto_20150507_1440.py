# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("config", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="config",
            name="category",
            field=models.CharField(
                max_length=1,
                choices=[
                    ("a", "to All"),
                    ("b", "to Users"),
                    ("c", "to EPFL Unit"),
                    ("d", "to LDAP Group"),
                ],
                default="a",
            ),
        ),
        migrations.AddField(
            model_name="config",
            name="enabled",
            field=models.BooleanField(default=True),
        ),
    ]
