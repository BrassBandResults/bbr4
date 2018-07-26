# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from django.contrib import admin

from bbr.admin import BbrAdmin
from users.models import UserProfile, PointsAward, UserBadge, \
    PersonalContestHistory, PersonalContestHistoryDateRange, UserNotification


class UserProfileAdmin(BbrAdmin):
    search_fields = ('user__username','user__email')
    list_display = ('__str__', 'rankings_access')
    fieldsets = (
        (None, {
                'fields' : ('user','points','display_name','contest_history_visibility','enhanced_functionality', 'pro_member', 'new_email_required')
                }),
        ("Payment", {
                'classes': ('collapse',),
                'fields' : ('stripe_email', 'stripe_token', 'stripe_customer', 'paypal_id', 'max_profile_count')
                       }),
        ("Superuser", {
                'classes': ('collapse',),
                'fields' : ('superuser','regional_superuser','regional_superuser_region','regional_superuser_regions',)
                       }),
    )

class PointsAwardAdmin(BbrAdmin):
    pass

class PasswordResetAdmin(BbrAdmin):
    pass

class PersonalContestHistoryAdmin(BbrAdmin):
    list_filter = ('user',)
    raw_id_fields = ("result",)

class PersonalContestHistoryDateRangeAdmin(BbrAdmin):
    list_filter = ('user',)
    
class UserNotificationAdmin(BbrAdmin):
    search_fields = ('notify_user__username',)
    list_display = ('__str__', 'notify_type', 'enabled', 'created', 'last_modified')
    list_filter = ('enabled',)
    
class UserBadgeAdmin(BbrAdmin):
    search_fields = ('user__username',)
    

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(PointsAward, PointsAwardAdmin)
admin.site.register(PersonalContestHistory, PersonalContestHistoryAdmin)
admin.site.register(PersonalContestHistoryDateRange, PersonalContestHistoryDateRangeAdmin)
admin.site.register(UserNotification, UserNotificationAdmin)
admin.site.register(UserBadge, UserBadgeAdmin)