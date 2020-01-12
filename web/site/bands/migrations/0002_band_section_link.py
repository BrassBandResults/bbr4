# -*- coding: utf-8 -*-
# Generated by Django 1.11.18 on 2020-01-12 16:29
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('sections', '0001_initial'),
        ('bands', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='band',
            name='section_link',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='sections.Section'),
        ),
    ]
