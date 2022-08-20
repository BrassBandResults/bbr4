# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved



from datetime import datetime

from django.contrib.auth.models import User
from django.db import models


class AuditEntry(models.Model):
    """
    An entry in the audit trail
    """
    created = models.DateTimeField(default=datetime.now,editable=False)
    subject = models.CharField(max_length=255)
    module = models.CharField(max_length=30)
    object_type = models.CharField(max_length=30)
    change_type = models.CharField(max_length=30)
    message = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, blank=True, null=True)
    useragent = models.CharField(max_length=1024, blank=True, null=True)
    address = models.CharField(max_length=16, blank=True, null=True)
    
    def __str__(self):
        return self.subject