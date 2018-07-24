# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved



from django import template

from users.models import UserBadge 


register = template.Library()

def badge_notifications_for_user(pUser):
    """
    Return any badge notifications for the current user, then delete them 
    """
    if pUser.is_anonymous() == True:
        return ''
    
    lBadgesToAward = UserBadge.objects.filter(user=pUser, notified=False)
    if len(lBadgesToAward) == 0:
        return ''
    lReturn = ''
    for lBadgeAward in lBadgesToAward:
        lReturn += "<span class='badgeAward'>Congratulations! You've been awarded the %s badge</span><br/>\n" % lBadgeAward.type.name
        lBadgeAward.notified = True
        lBadgeAward.save()
    return lReturn 
        
register.simple_tag(badge_notifications_for_user)
