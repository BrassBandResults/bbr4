# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved



from datetime import datetime, date

from django.contrib.auth.models import User
from django.db import models

class PlayerPosition(models.Model):
    """
    Available player positions for vacancies
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=date.today,editable=False)
    name = models.CharField(max_length=50, help_text="Name of band position")
    SECTION_CHOICES = (
                       ('md','Conductor'),
                       ('pc','Principal Cornet'),
                       ('fc','Front Row Cornet'),
                       ('cc','Cornet'),
                       ('sc','Soprano Cornet'),
                       ('bc','Back Row Cornet'),
                       ('fh','Flugel Horn'),
                       ('h','Horn'),
                       ('be','Baritone/Euphonium'),
                       ('tt','Trombones'),
                       ('bs','Basses'),
                       ('pc','Percussion'),
                       )
    section = models.CharField(max_length=2, choices=SECTION_CHOICES, help_text="Section in the band this position is from")
    lastChangedBy = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='PlayerPositionLastChangedBy')
    owner = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='PlayerPositionOwner')
    
    def __str__(self):
        return " %s" % (self.name)
    
    def save(self, force_insert=False, force_update=False, using=None):
        self.last_modified = datetime.now()
        super(PlayerPosition, self).save(force_insert, force_update, using)   
        
    class meta:
        ordering = ('name')