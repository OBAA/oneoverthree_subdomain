# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-12-03 13:58
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_order_discount'),
    ]

    operations = [
        migrations.RenameField(
            model_name='order',
            old_name='discount',
            new_name='discount_applied',
        ),
    ]
