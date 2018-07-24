# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved

from datetime import datetime

from django.contrib.auth.models import User
from django.db import models

from bands.models import Band
from contests.models import Venue
from people.models import Person
from pieces.models import TestPiece


class BandMergeRequest(models.Model):
    """
    A request to merge one band into another
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    source_band = models.ForeignKey(Band, related_name='BandFrom', on_delete=models.deletion.CASCADE)
    destination_band = models.ForeignKey(Band, related_name='BandTo', on_delete=models.deletion.CASCADE)
    lastChangedBy = models.ForeignKey(User, editable=False, related_name='BandMergeLastChangedBy',blank=True,null=True)
    owner = models.ForeignKey(User, editable=True, related_name='BandMergeOwner',blank=True,null=True)
    
    def __str__(self):
        return "%s->%s" % (self.source_band.name, self.destination_band.name)
    
    def save(self):
        self.last_modified = datetime.now()
        super(BandMergeRequest, self).save()
        
    class Meta:
        ordering = ['created']

        
        
class PersonMergeRequest(models.Model):
    """
    A request to merge one person into another
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    source_person = models.ForeignKey(Person, related_name='PersonFrom')
    destination_person = models.ForeignKey(Person, related_name='PersonTo')
    lastChangedBy = models.ForeignKey(User, editable=False, related_name='PersonMergeLastChangedBy',blank=True,null=True)
    owner = models.ForeignKey(User, editable=True, related_name='PersonMergeOwner',blank=True,null=True)
    
    def __str__(self):
        return "%s->%s" % (self.source_person.name, self.destination_person.name)
    
    def save(self):
        self.last_modified = datetime.now()
        super(PersonMergeRequest, self).save()
        
    class Meta:
        ordering = ['created']
        
        

        
class VenueMergeRequest(models.Model):
    """
    A request to merge one venue into another
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    source_venue = models.ForeignKey(Venue, related_name='VenueFrom')
    destination_venue = models.ForeignKey(Venue, related_name='VenueTo')
    lastChangedBy = models.ForeignKey(User, editable=False, related_name='VenueMergeLastChangedBy',blank=True,null=True)
    owner = models.ForeignKey(User, editable=True, related_name='VenueMergeOwner',blank=True,null=True)
    
    def __str__(self):
        return "%s->%s" % (self.source_venue.name, self.destination_venue.name)
    
    def save(self):
        self.last_modified = datetime.now()
        super(VenueMergeRequest, self).save()
        
    class Meta:
        ordering = ['created']   
        
        
class PieceMergeRequest(models.Model):
    """
    A request to merge one test piece into another
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    source_piece = models.ForeignKey(TestPiece, related_name='PieceFrom')
    destination_piece = models.ForeignKey(TestPiece, related_name='PieceTo')
    lastChangedBy = models.ForeignKey(User, editable=False, related_name='PieceMergeLastChangedBy',blank=True,null=True)
    owner = models.ForeignKey(User, editable=True, related_name='PieceMergeOwner',blank=True,null=True)
    
    def __str__(self):
        return "%s->%s" % (self.source_piece.name, self.destination_piece.name)
    
    def save(self):
        self.last_modified = datetime.now()
        super(PieceMergeRequest, self).save()
        
    class Meta:
        ordering = ['created'] 
        
