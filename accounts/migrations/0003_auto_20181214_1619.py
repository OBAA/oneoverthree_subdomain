# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-12-14 15:19
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_auto_20181214_1518'),
    ]

    operations = [
        migrations.RenameField(
            model_name='user',
            old_name='mobile_num',
            new_name='mobile_number',
        ),
    ]