# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-12-15 10:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_auto_20181215_1130'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='mobile_number',
            field=models.CharField(max_length=12, unique=True),
        ),
    ]