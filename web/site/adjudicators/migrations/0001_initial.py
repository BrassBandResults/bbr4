# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-08-15 19:49
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contests', '__first__'),
        ('people', '__first__'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContestAdjudicator',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_modified', models.DateTimeField(default=datetime.datetime.now, editable=False)),
                ('created', models.DateTimeField(default=datetime.datetime.now, editable=False)),
                ('adjudicator_name', models.CharField(blank=True, help_text='Original adjudicator name entered', max_length=100, null=True)),
                ('contest_event', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contests.ContestEvent')),
                ('lastChangedBy', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='ContestAdjudicatorLastChangedBy', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(editable=False, on_delete=django.db.models.deletion.CASCADE, related_name='ContestAdjudicatorOwner', to=settings.AUTH_USER_MODEL)),
                ('person', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='people.Person')),
            ],
            options={
                'ordering': ['contest_event'],
            },
        ),
    ]
