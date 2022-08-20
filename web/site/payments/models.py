# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved



from django.db import models
from datetime import datetime
from users.models import UserProfile

class UserPayment(models.Model):
    """
    Details about a payment made by a user
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    user_profile = models.ForeignKey(UserProfile, on_delete=models.PROTECT)
    payment_date = models.DateField()
    gross_amount = models.DecimalField(max_digits=5, decimal_places=2)
    net_amount = models.DecimalField(max_digits=5, decimal_places=2)
            
    def __str__(self):
        return "%s %s" % (self.created, self.user_profile.user.username)
    
    def save(self):
        self.last_modified = datetime.now()
        super(UserPayment, self).save()
        
    class Meta:
        ordering = ['-payment_date','user_profile__user__username']
        