# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved

from django.db import models
from datetime import datetime
from django.contrib.auth.models import User

class Section(models.Model):
    """
    A brass band national contesting section
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    name = models.CharField(max_length=100)
    position = models.IntegerField(default=0, help_text='Position to show in list')
    slug = models.SlugField()
    short_code = models.CharField(max_length=1, blank=True, null=True)
    lastChangedBy = models.ForeignKey(User, editable=False, related_name='SectionLastChangedBy')
    owner = models.ForeignKey(User, editable=False, related_name='SectionOwner')
    
        
    def __str__(self):
        return "%s" % (self.name)
    
    @property
    def next(self):
        return Section.objects.filter(position__gt=self.position).order_by('position')[0]
        
    @property
    def previous(self):
        return Section.objects.filter(position__lt=self.position).order_by('-position')[0]
        
    def save(self):
        self.last_modified = datetime.now()
        super(Section, self).save()
    
    class Meta:
        ordering = ['position']