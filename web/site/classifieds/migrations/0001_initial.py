# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-08-15 19:50
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PlayerPosition',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_modified', models.DateTimeField(default=datetime.datetime.now, editable=False)),
                ('created', models.DateTimeField(default=datetime.date.today, editable=False)),
                ('name', models.CharField(help_text='Name of band position', max_length=50)),
                ('section', models.CharField(choices=[('md', 'Conductor'), ('pc', 'Principal Cornet'), ('fc', 'Front Row Cornet'), ('cc', 'Cornet'), ('sc', 'Soprano Cornet'), ('bc', 'Back Row Cornet'), ('fh', 'Flugel Horn'), ('h', 'Horn'), ('be', 'Baritone/Euphonium'), ('tt', 'Trombones'), ('bs', 'Basses'), ('pc', 'Percussion')], help_text='Section in the band this position is from', max_length=2)),
                ('lastChangedBy', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='PlayerPositionLastChangedBy', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='PlayerPositionOwner', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
