# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2019-01-02 09:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0006_auto_20181215_1410'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailactivation',
            name='coupon',
            field=models.CharField(blank=True, max_length=120, null=True),
        ),
    ]
