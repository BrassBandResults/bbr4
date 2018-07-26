# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from django.contrib import admin

from bbr.admin import BbrAdmin
from feedback.models import SiteFeedback, ClarificationRequest


class SiteFeedbackAdmin(BbrAdmin):
    pass

class ClarificationRequestAdmin(BbrAdmin):
    pass

admin.site.register(SiteFeedback, SiteFeedbackAdmin)
admin.site.register(ClarificationRequest, ClarificationRequestAdmin)