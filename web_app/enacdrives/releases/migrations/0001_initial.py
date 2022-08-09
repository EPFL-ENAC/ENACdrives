# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Arch",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        serialize=False,
                        verbose_name="ID",
                        primary_key=True,
                    ),
                ),
                (
                    "os",
                    models.CharField(
                        default="a",
                        max_length=1,
                        choices=[("a", "Windows"), ("b", "Linux"), ("c", "MacOSX")],
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Installer",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        serialize=False,
                        verbose_name="ID",
                        primary_key=True,
                    ),
                ),
                ("upload_username", models.CharField(max_length=256)),
                ("upload_date", models.DateTimeField()),
                ("release_number", models.CharField(max_length=256)),
                ("file_name", models.CharField(max_length=256)),
                ("storage_name", models.CharField(max_length=256)),
                ("arch", models.ForeignKey(to="releases.Arch")),
            ],
        ),
        migrations.AddField(
            model_name="arch",
            name="current_installer",
            field=models.ForeignKey(
                related_name="+", null=True, blank=True, to="releases.Installer"
            ),
        ),
        migrations.AlterUniqueTogether(
            name="arch",
            unique_together=set([("os",)]),
        ),
    ]
