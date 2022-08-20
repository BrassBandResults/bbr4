# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved



from django.db import models
from datetime import datetime
from django.contrib.auth.models import User

class SiteFeedback(models.Model):
    """
    Feedback that has been provided
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    url = models.CharField(max_length=255)
    comment = models.TextField()
    STATUS_CHOICES = (
                      ('Outstanding', 'Feedback Outstanding'),
                      ('Done', 'Feedback Complete'),
                      ('Queue', 'In Superuser Feedback Queue'),
                      ('Admin', 'In Admin Feedback Queue'),
                      ('Inconclusive', 'Not Enough Info'),
                      )
    status = models.CharField(max_length=20, blank=True, null=True, choices=STATUS_CHOICES, default='Queue')
    claim_date = models.DateTimeField(default=None, blank=True, null=True)
    additional_comments = models.TextField(blank=True, null=True)
    ip = models.GenericIPAddressField()
    browser_id = models.CharField(max_length=1024)
    reporter = models.ForeignKey(User, on_delete=models.PROTECT, blank=True, null=True)
    audit_log = models.TextField(blank=True, null=True)
    lastChangedBy = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='FeedbackLastChangedBy')
    owner = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='FeedbackOwner')
        
    def __str__(self):
        return "%s (%s)" % (self.url, self.status)
    
    def save(self, pAuditText=None):
        if pAuditText:
            if self.audit_log == None:
                self.audit_log = ""
            self.audit_log += "%s %s\n" % (datetime.now(), pAuditText) 
        self.last_modified = datetime.now()
        super(SiteFeedback, self).save()
        
    @property
    def status_display(self):
        return self.status
            
    
    class Meta:
        ordering = ['created']
        

class ClarificationRequest(models.Model):
    """
    A request for help from the site users
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    comment = models.TextField()
    hidden = models.BooleanField(default=False)
        
    def __str__(self):
        return "%d - %s" % (self.id, self.comment[:50])
    
    def save(self):
        self.last_modified = datetime.now()
        super(ClarificationRequest, self).save()
        
    class Meta:
        ordering = ['created']              