# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved

from datetime import datetime

from django.contrib.auth.models import User
from django.db import models


class Message(models.Model):
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    from_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='MessagesFrom')
    to_user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='MessagesTo')
    deleted = models.BooleanField(default=False)
    read = models.BooleanField(default=False)
    title = models.CharField(max_length=255)
    text = models.TextField()
    lastChangedBy = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='MessageLastChangedBy',blank=True,null=True)
    owner = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='MessageOwner',blank=True,null=True)
    
    def __str__(self):
        return "%s->%s - %s" % (self.from_user.username, self.to_user.username, self.title)
    
    def save(self):
        self.last_modified = datetime.now()
        super(Message, self).save()
        
    class Meta:
        ordering = ['-created']
        db_table = 'messages_message'
