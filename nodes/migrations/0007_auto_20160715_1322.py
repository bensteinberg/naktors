# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-15 13:22
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('nodes', '0006_auto_20160714_1341'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='nodeclass',
            options={'verbose_name_plural': 'node classes'},
        ),
        migrations.AlterField(
            model_name='node',
            name='actor_urn',
            field=models.CharField(blank=True, max_length=200, null=True),
        ),
    ]
