# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-12-03 12:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0003_auto_20181203_1256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='couponcode',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
