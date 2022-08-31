# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Config",
            fields=[
                (
                    "id",
                    models.AutoField(
                        primary_key=True,
                        serialize=False,
                        auto_created=True,
                        verbose_name="ID",
                    ),
                ),
                ("rank", models.IntegerField(default=0)),
                ("name", models.CharField(max_length=256)),
                ("data", models.TextField(blank=True)),
            ],
        ),
        migrations.CreateModel(
            name="EpflUnit",
            fields=[
                (
                    "id",
                    models.AutoField(
                        primary_key=True,
                        serialize=False,
                        auto_created=True,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name="LdapGroup",
            fields=[
                (
                    "id",
                    models.AutoField(
                        primary_key=True,
                        serialize=False,
                        auto_created=True,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name="User",
            fields=[
                (
                    "id",
                    models.AutoField(
                        primary_key=True,
                        serialize=False,
                        auto_created=True,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=256)),
            ],
        ),
        migrations.AddField(
            model_name="config",
            name="epfl_units",
            field=models.ManyToManyField(blank=True, to="config.EpflUnit"),
        ),
        migrations.AddField(
            model_name="config",
            name="ldap_groups",
            field=models.ManyToManyField(blank=True, to="config.LdapGroup"),
        ),
        migrations.AddField(
            model_name="config",
            name="users",
            field=models.ManyToManyField(blank=True, to="config.User"),
        ),
    ]
