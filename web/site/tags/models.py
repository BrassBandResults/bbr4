# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from datetime import datetime

from django.contrib.auth.models import User
from django.db import models

from bbr.siteutils import slugify


class ContestTag(models.Model):
    """
    Tag that can be linked to a contest or contest group
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    lastChangedBy = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='ContestTagLastChangedBy')
    owner = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='ContestTagOwner')
        
    def __str__(self):
        return "%s" % (self.name)
    
    def save(self):
        if len(self.slug) == 0:
            self.slug = slugify(self.name)
        self.last_modified = datetime.now()
        super(ContestTag, self).save()
    
    class Meta:
        ordering = ['name']   