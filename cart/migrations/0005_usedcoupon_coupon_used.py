# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-12-04 10:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cart', '0004_auto_20181203_1316'),
    ]

    operations = [
        migrations.AddField(
            model_name='usedcoupon',
            name='coupon_used',
            field=models.BooleanField(default=False),
        ),
    ]