# -*- coding: utf-8 -*-
# Generated by Django 1.11.15 on 2018-08-15 19:51
from __future__ import unicode_literals

import datetime
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('pieces', '__first__'),
        ('contests', '0001_initial'),
        ('people', '__first__'),
        ('bands', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BandMergeRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_modified', models.DateTimeField(default=datetime.datetime.now, editable=False)),
                ('created', models.DateTimeField(default=datetime.datetime.now, editable=False)),
                ('destination_band', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='BandTo', to='bands.Band')),
                ('lastChangedBy', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='BandMergeLastChangedBy', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='BandMergeOwner', to=settings.AUTH_USER_MODEL)),
                ('source_band', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='BandFrom', to='bands.Band')),
            ],
            options={
                'ordering': ['created'],
            },
        ),
        migrations.CreateModel(
            name='PersonMergeRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_modified', models.DateTimeField(default=datetime.datetime.now, editable=False)),
                ('created', models.DateTimeField(default=datetime.datetime.now, editable=False)),
                ('destination_person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='PersonTo', to='people.Person')),
                ('lastChangedBy', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='PersonMergeLastChangedBy', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='PersonMergeOwner', to=settings.AUTH_USER_MODEL)),
                ('source_person', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='PersonFrom', to='people.Person')),
            ],
            options={
                'ordering': ['created'],
            },
        ),
        migrations.CreateModel(
            name='PieceMergeRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_modified', models.DateTimeField(default=datetime.datetime.now, editable=False)),
                ('created', models.DateTimeField(default=datetime.datetime.now, editable=False)),
                ('destination_piece', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='PieceTo', to='pieces.TestPiece')),
                ('lastChangedBy', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='PieceMergeLastChangedBy', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='PieceMergeOwner', to=settings.AUTH_USER_MODEL)),
                ('source_piece', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='PieceFrom', to='pieces.TestPiece')),
            ],
            options={
                'ordering': ['created'],
            },
        ),
        migrations.CreateModel(
            name='VenueMergeRequest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('last_modified', models.DateTimeField(default=datetime.datetime.now, editable=False)),
                ('created', models.DateTimeField(default=datetime.datetime.now, editable=False)),
                ('destination_venue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='VenueTo', to='contests.Venue')),
                ('lastChangedBy', models.ForeignKey(blank=True, editable=False, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='VenueMergeLastChangedBy', to=settings.AUTH_USER_MODEL)),
                ('owner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='VenueMergeOwner', to=settings.AUTH_USER_MODEL)),
                ('source_venue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='VenueFrom', to='contests.Venue')),
            ],
            options={
                'ordering': ['created'],
            },
        ),
    ]
