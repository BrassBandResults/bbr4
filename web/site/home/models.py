# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from datetime import datetime

from django.contrib.auth.models import User
from django.db import models


class FaqSection(models.Model):
    """
    A section grouping FAQ Entries
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    name = models.CharField(max_length=255)
    position = models.IntegerField()
    lastChangedBy = models.ForeignKey(User, editable=False, related_name='FaqSectionLastChangedBy')
    owner = models.ForeignKey(User, editable=False, related_name='FaqSectionOwner')
        
    def __str__(self):
        return "%s" % (self.name)
    
    def save(self):
        self.last_modified = datetime.now()
        super(FaqSection, self).save()
    
    class Meta:
        ordering = ['position']   

class FaqEntry(models.Model):
    """
    A question and answer from the FAQ section
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    question = models.TextField()
    answer = models.TextField()
    position = models.IntegerField()
    section = models.ForeignKey(FaqSection)
    lastChangedBy = models.ForeignKey(User, editable=False, related_name='FaqEntryLastChangedBy')
    owner = models.ForeignKey(User, editable=False, related_name='FaqEntryOwner')
        
    def __str__(self):
        return "%s" % self.question
    
    def save(self):
        self.last_modified = datetime.now()
        super(FaqEntry, self).save()
    
    class Meta:
        ordering = ['section__position', 'position']   