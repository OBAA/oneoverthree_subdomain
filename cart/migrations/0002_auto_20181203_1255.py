# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-12-03 11:55
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='couponcode',
            name='amount',
            field=models.IntegerField(null=True),
        ),
    ]
