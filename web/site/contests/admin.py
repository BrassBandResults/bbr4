# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from django.contrib import admin

from adjudicators.models import ContestAdjudicator
from bbr.admin import BbrAdmin
from contests.models import Contest, ContestEvent, ContestResult, \
    ContestWeblink, ContestGroup, ContestGroupAlias, ContestAlias, \
    ContestGroupWeblink, ContestProgrammePage, ContestProgrammeCover, \
    ContestTestPiece, ContestType, ContestAchievementAward, ContestEventWeblink, ContestGroupLinkEventLink, \
    ContestTalkPage, GroupTalkPage, ResultPiecePerformance


class WebsiteInline(admin.TabularInline):
    model = ContestWeblink

class GroupWebsiteInline(admin.TabularInline):
    model = ContestGroupWeblink

class ContestAliasInline(admin.TabularInline):
    model = ContestAlias

class ContestEventContestLinkInline(admin.TabularInline):
    model = ContestGroupLinkEventLink
    raw_id_fields = ("event",)

class ContestAdmin(BbrAdmin):
    prepopulated_fields = {"slug" : ("name",)}
    inlines = [ContestAliasInline, WebsiteInline, ContestEventContestLinkInline]
    search_fields = ['name']

class AdjudicatorInline(admin.TabularInline):
    model = ContestAdjudicator

class ContestEventWeblinkInline(admin.TabularInline):
    model = ContestEventWeblink

class ResultsInline(admin.TabularInline):
    model = ContestResult

class ContestTypeAdmin(BbrAdmin):
    pass

class ContestEventAdmin(BbrAdmin):
    search_fields = ('contest__name',)
    inlines = [AdjudicatorInline, ContestEventWeblinkInline]


class ContestResultAdmin(BbrAdmin):
    list_filter = ('results_position',)
    list_per_page = 500
    ordering = ('-contest_event__date_of_event', 'results_position')
    search_fields = ('band__name', 'contest_event__contest__name')
    readonly_fields = ('conductor_name',)
    fieldsets = (
        (None, {
                'fields' : ('band','band_name','person_conducting','second_person_conducting', 'conductor_name','results_position','draw','points','test_piece','notes')
                }),
        ("Extended Draw and Points", {
                'classes': ('collapse',),
                'fields' : ('draw_second_part','points_first_part','points_second_part','points_third_part','points_fourth_part','penalty_points')
                             })
    )
    raw_id_fields = ("band", "person_conducting", "second_person_conducting", "test_piece")



class ContestGroupAliasInline(admin.TabularInline):
    model = ContestGroupAlias

class ContestGroupAdmin(BbrAdmin):
    prepopulated_fields = {"slug" : ("name",)}
    inlines = [ContestGroupAliasInline, GroupWebsiteInline]

class ProgrammePageAdmin(admin.TabularInline):
    model = ContestProgrammePage

class ContestProgrammeCoverAdmin(BbrAdmin):
    search_fields = ['contest_group__name', 'contest__name']
    inlines = [ProgrammePageAdmin, ]

class ContestTestPieceAdmin(BbrAdmin):
    raw_id_fields = ("contest_event","test_piece")

class ContestAchievementAwardAdmin(admin.ModelAdmin):
    list_display = ('award', 'year_of_award', 'contest', 'band', 'band_name')

class GroupTalkPageAdmin(BbrAdmin):
    pass

class ContestTalkPageAdmin(BbrAdmin):
    pass

class ResultPiecePerformanceAdmin(BbrAdmin):
    raw_id_fields = ('result',)
    list_display = ('__str__', 'suffix')

admin.site.register(Contest, ContestAdmin)
admin.site.register(ContestType, ContestTypeAdmin)
admin.site.register(ContestEvent, ContestEventAdmin)
admin.site.register(ContestResult, ContestResultAdmin)
admin.site.register(ContestGroup, ContestGroupAdmin)
admin.site.register(ContestProgrammeCover, ContestProgrammeCoverAdmin)
admin.site.register(ContestTestPiece, ContestTestPieceAdmin)
admin.site.register(ContestAchievementAward, ContestAchievementAwardAdmin)
admin.site.register(ContestTalkPage, ContestTalkPageAdmin)
admin.site.register(GroupTalkPage, GroupTalkPageAdmin)
admin.site.register(ResultPiecePerformance, ResultPiecePerformanceAdmin)
