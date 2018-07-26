# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from django.contrib import admin
from django.contrib.auth.models import User

from bbr.admin import BbrAdmin
from usermessages.models import Message


class MessageAdmin(BbrAdmin):
    search_fields = ('title','text')
    foreignkey_filters =  {
                          'from_user' : lambda site : User.objects.filter(username__endswith='_%s' % (site.sitedata_set.all()[0].site_short_name)).order_by('username'),
                          'to_user' : lambda site : User.objects.filter(username__endswith='_%s' % (site.sitedata_set.all()[0].site_short_name)).order_by('username'),
                          }
    
admin.site.register(Message, MessageAdmin)