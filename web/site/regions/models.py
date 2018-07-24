# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved



from datetime import datetime

from django.contrib.auth.models import User
from django.contrib.gis.db import models as geomodels
from django.contrib.gis.geos.factory import fromstr
from django.db import models


class Region(models.Model):
    """
    A brass band national contesting region
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    name = models.CharField(max_length=100)
    container = models.ForeignKey('Region', blank=True, null=True, help_text='Containing Region')
    latitude = models.CharField(max_length=15, blank=True, null=True, help_text="Center location for region map")
    longitude = models.CharField(max_length=15, blank=True, null=True, help_text="Center location for region map") 
    default_map_zoom = models.IntegerField(blank=True, null=True)
    point = geomodels.PointField(dim=3, geography=True, blank=True, null=True, editable=False)
    slug = models.SlugField()
    country_code = models.CharField(max_length=20, blank=True, null=True)
    seed_contest_group_slug = models.CharField(max_length=50, blank=True, null=True)
    lastChangedBy = models.ForeignKey(User, editable=False, related_name='RegionLastChangedBy')
    owner = models.ForeignKey(User, editable=False, related_name='RegionOwner')
    
    def __str__(self):
        return "%s" % (self.name)
    
    def get_absolute_url(self):
        return "/regions/%s/" % self.slug      
    
    def is_great_britain(self):
        try:
            return self.container.name == 'Great Britain'
        except:
            return False
    
    def save(self):
        if self.latitude != None and len(self.latitude) > 0:
            lString = 'POINT(%s %s)' % (self.longitude.strip(), self.latitude.strip())
            self.map_location = fromstr(lString)
            self.point = fromstr(lString)
        self.last_modified = datetime.now()
        super(Region, self).save()
    
    class Meta:
        ordering = ['name']        
        