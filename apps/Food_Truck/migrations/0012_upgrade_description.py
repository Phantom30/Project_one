# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2018-07-25 23:56
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('Food_Truck', '0011_merge_20180725_1656'),
    ]

    operations = [
        migrations.AddField(
            model_name='upgrade',
            name='description',
            field=models.CharField(max_length=255, null=True),
        ),
    ]
