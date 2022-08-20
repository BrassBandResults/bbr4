# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved

from datetime import datetime

from django.db import models

from bands.models import Band


class EmbeddedResultsLog(models.Model):
    """
    Class used to log accesses to the embedded results page
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    band_slug = models.CharField(max_length=50)
    band = models.ForeignKey(Band, on_delete=models.CASCADE, null=True, blank=True)
    ip = models.GenericIPAddressField()
    browser_id = models.CharField(max_length=1024)
    referer = models.CharField(max_length=255, blank=True, null=True)
    
    def save(self):
        self.last_modified = datetime.now()
        super(EmbeddedResultsLog, self).save()
    
    