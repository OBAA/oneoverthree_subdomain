# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-12-04 09:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_auto_20181203_1458'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='pdf_sent',
            field=models.BooleanField(default=False),
        ),
    ]
