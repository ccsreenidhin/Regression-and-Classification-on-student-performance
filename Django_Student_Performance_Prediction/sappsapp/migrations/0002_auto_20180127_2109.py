# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-01-27 15:39
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sappsapp', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='profilechild',
            name='parent',
        ),
        migrations.AddField(
            model_name='profileparent',
            name='child',
            field=models.OneToOneField(default='', on_delete=django.db.models.deletion.CASCADE, to='sappsapp.Profilechild'),
            preserve_default=False,
        ),
    ]
