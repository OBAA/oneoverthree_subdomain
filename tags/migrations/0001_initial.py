# -*- coding: utf-8 -*-
# Generated by Django 1.11.4 on 2018-11-11 17:15
from __future__ import unicode_literals

from django.db import migrations, models
import tags.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=120)),
                ('slug', models.SlugField(blank=True)),
                ('background_image', models.ImageField(blank=True, null=True, upload_to=tags.models.upload_image_path)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('ordering', models.IntegerField(default=20)),
                ('is_active', models.BooleanField(default=True)),
                ('is_banner', models.BooleanField(default=False)),
            ],
            options={
                'ordering': ['title'],
            },
        ),
    ]
