# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved



from datetime import datetime

from django.db import models


class Badge(models.Model):
    """
    A badge available to award
    """
    WON_CONTEST = 1 # won a contest
    #WON_HAT_TRICK = 2 # won a hatrick of results at a contest
    #WON_TOP_SECTION_AREA = 3 # won a championship section area
    #WON_LOWER_SECTION_AREA = 4 # won a lower section area
    #WON_TOP_SECTION__NATIONAL_FINAL = 5 # won a championship section national final
    #WON_LOWER_SECTION_NATIONAL_FINAL = 6 # won a lower section national final
    #WON_GRAND_SLAM = 7 # won nationals, open and european in same year
    #WON_DOUBLE = 8 # won nationals and open in same year
    CARTOGRAPHER = 9 # has moved a band on the map
    MASTER_MAPPER = 10 # has moved 10 bands on the map 
    VENUE_CARTOGRAPHER = 11 # has moved a venue on the map
    COMPETITOR = 12 # has created a personal contest history
    CONTRIBUTOR = 13 # has added a result
    PROGRAMME_SCANNER = 14 # has uploaded programme cover
    SCHEDULER = 15 # has created a future event
    
    # Local Nationals & European Double Win
    # has added 50 results
    
    
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    name = models.CharField(max_length=100)
    BADGE_TYPE_CHOICES = (
                          ('B', 'Band'),
                          ('U', 'User'),
                          )
    type = models.CharField(max_length=1, choices=BADGE_TYPE_CHOICES, default='U')
    LEVEL_CHOICES = (
                          ('B', 'Bronze'),
                          ('S', 'Silver'),
                          ('G', 'Gold'),
                          )
    level = models.CharField(max_length=1, choices=LEVEL_CHOICES, default='B')
    description = models.CharField(max_length=1024, blank=True, null=True)
        
    def __str__(self):
        return "%s" % (self.name)
    
    def save(self, force_insert=False, force_update=False, using=None):
        self.last_modified = datetime.now()
        super(Badge, self).save(force_insert, force_update, using)        