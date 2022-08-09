# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ("config", "0002_auto_20150507_1440"),
    ]

    operations = [
        migrations.AlterField(
            model_name="config",
            name="category",
            field=models.CharField(
                default="d",
                choices=[
                    ("a", "to All"),
                    ("b", "to Users"),
                    ("c", "to EPFL Unit"),
                    ("d", "to LDAP Group"),
                ],
                max_length=1,
            ),
        ),
    ]
