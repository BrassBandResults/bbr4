# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved



import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.gis.geos import Point
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.db import connection
from django.db.models import Q 
from django.http import Http404, HttpResponseRedirect, HttpResponsePermanentRedirect
from django.shortcuts import get_object_or_404
from django.utils.datastructures import MultiValueDictKeyError
from django.views.decorators.csrf import csrf_exempt

from adjudicators.models import ContestAdjudicator
from bands.models import Band
from bbr.decorators import login_required_pro_user
from bbr.siteutils import browser_details, slugify
from bbr.render import render_auth
from bbr.talkutils import fetch_recent_talk_changes
from classifieds.models import PlayerPosition
from contests.forms import ContestResultForm, ContestEventForm, FutureEventForm, FutureEventFormNoContest, ContestProgrammeCoverForm, ContestForm, ContestTalkEditForm, GroupTalkEditForm
from contests.models import Contest, ContestEvent, ContestResult, ContestGroup, ContestGroupAlias, ContestAlias, ContestProgrammeCover, ContestTestPiece, ContestProgrammePage, ContestAchievementAward, ContestEventWeblink, ContestTalkPage, GroupTalkPage, ResultPiecePerformance
from bbr.notification import notification
from people.models import Person, PersonAlias
from pieces.models import TestPiece, TestPieceAlias
from regions.models import Region
from users.models import PersonalContestHistory


def contest_list(request):
    """
    Show list of contests beginning with A
    """
    return contest_list_filter_letter(request, 'A')

def contest_list_filter_letter(request, pLetter):
    """
    Show list of contests beginning with specified letter
    """
    lContests = Contest.objects.filter(group=None)
    lContestAliases = ContestAlias.objects.all()
    lContestGroups = ContestGroup.objects.all()
    lContestGroupAliases = ContestGroupAlias.objects.all().select_related()
    if pLetter != 'ALL':
        lContests = lContests.filter(name__istartswith=pLetter)
        lContestAliases = lContestAliases.filter(name__istartswith=pLetter)
        lContestGroups = lContestGroups.filter(name__istartswith=pLetter)
        lContestGroupAliases = lContestGroupAliases.filter(name__istartswith=pLetter)
        
        
    lContestsToShow = []
    for contest in lContests:
        lContestsToShow.append(contest)
    for contest_alias in lContestAliases:
        lContestsToShow.append(contest_alias)
    for contest_group in lContestGroups:
        lContestsToShow.append(contest_group)
    for contest_group_alias in lContestGroupAliases:
        lContestsToShow.append(contest_group_alias)
    return render_auth(request, 'contests/contests.html', {"Contests" : lContestsToShow,
                                                           "StartsWith" : pLetter,
                                                           })

def single_contest(request, pContestSlug):
    """
    Show events for a single contest
    """
    # get contest
    try:
        lContest = Contest.objects.filter(slug=pContestSlug).select_related('qualifies_for')[0]
    except IndexError:
        raise Http404
    
    lShowTabs = False
    
    # get contest events
    cursor = connection.cursor()
    lEvents = []
    lEventIds = ""
    cursor.execute("SELECT * FROM (SELECT event.date_of_event, event.name, contest.slug, contest.name, event.id, contest.id, contest.description, contest.contact_info, contest.notes, contest.extinct, event.date_resolution, contest.group_id, event.test_piece_id, event.no_contest, event.notes, 'DIRECT' FROM contests_contest contest INNER JOIN contests_contestevent event ON event.contest_id = contest.id WHERE contest.id = '%s' AND event.date_of_event < now() UNION SELECT event.date_of_event, event.name, contest.slug, contest.name, event.id, contest.id, contest.description, contest.contact_info, contest.notes, contest.extinct, event.date_resolution, contest.group_id, event.test_piece_id, event.no_contest, event.notes, 'LINK' FROM contests_contest contest INNER JOIN contests_contestevent event ON event.contest_id = contest.id WHERE event.id IN (SELECT event_id FROM contests_contestgrouplinkeventlink WHERE contest_id = '%s') AND event.date_of_event < now() ) x ORDER BY 1 desc" % (lContest.id, lContest.id))
    rows = cursor.fetchall()
    lFetchWinners = (len(rows) > 0)
    lTestPieceSerials = []
    for row in rows:
        lEvent = ContestEvent()
        lEvent.date_of_event = row[0]
        lEvent.name = row[1]
        lContestSlug = row[2]
        lEvent.contest_slug = lContestSlug
        lContestName = row[3]
        lEvent.id = row[4]
        lContestId = row[5]
        lContestDescription = row[6]
        lContestContactInfo = row[7]
        lContestNotes = row[8]
        lContestExtinct = row[9]
        lEvent.date_resolution = row[10]
        lContestGroupId = row[11]
        lEvent.test_piece_id = row[12]
        lEvent.no_contest = row[13]
        lEvent.notes = row[14]
        lEvent.link_type = row[15] # DIRECT or LINK
        lTestPieceSerials.append(lEvent.test_piece_id)
        if len(lEventIds) > 0:
            lEventIds += ','
        lEventIds += str(lEvent.id)
        lEvents.append(lEvent)
    cursor.close()
    
    if lFetchWinners:
        # get winners
        cursor = connection.cursor()
        lWinners = {}
        cursor.execute("select result.contest_event_id, result.band_name, result.band_id, band.slug, band.name, region.name, region.country_code, result.test_piece_id, conductor.slug, conductor.first_names || ' ' || conductor.surname || ' ' || coalesce(conductor.suffix,'')  from contests_contestresult result, bands_band band, regions_region region, people_person conductor where result.band_id = band.id and result.person_conducting_id = conductor.id and band.region_id = region.id and result.results_position = 1 and result.contest_event_id in (%s)" % lEventIds)
        rows = cursor.fetchall() 
        for row in rows:
            try:
                lExistingWinners = lWinners[row[0]]
                lExistingWinners.append((row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9]))
                lWinners[row[0]] = lExistingWinners
            except KeyError:
                lWinners[row[0]] = [(row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9])]
        cursor.close()
    
        for lEvent in lEvents:
            lEvent.winners = []
            if lEvent.id in lWinners.keys():
                for winner in lWinners[lEvent.id]:
                    lBand = Band()
                    lBand.id = winner[1]
                    lBand.slug = winner[2]
                    lBand.name = winner[3]
                    lBand.band_name = winner[0]
                    lBand.region = Region()
                    lBand.region.name = winner[4]
                    lBand.region.country_code = winner[5] 
                    lBand.own_choice_id = winner[6]
                    if lBand.own_choice_id:
                        lTestPieceSerials.append(lBand.own_choice_id)
                    lBand.conductor_slug = winner[7]
                    lBand.conductor_name = winner[8].strip()
                    lEvent.winners.append(lBand)
    
    # Test Pieces
    lPieces = TestPiece.objects.filter(id__in=lTestPieceSerials)
    for event in lEvents:
        for piece in lPieces:
            if event.test_piece_id == piece.id:
                event.test_piece = piece
                break
        if event.test_piece is None:
            for piece in lPieces:
                try:
                    for winner in event.winners:
                        if winner.own_choice_id == piece.id:
                            winner.test_piece = piece
                            continue
                except AttributeError:
                    pass # no winner
            
    # Future Events
    lToday = datetime.date.today()
    lFutureEvents = ContestEvent.objects.filter(contest__id=lContest.id).filter(date_of_event__gte=lToday).order_by('date_of_event').exclude(no_contest=True)
    if lFutureEvents.count() == 0:
        lFutureEvents = None
        
    # Own choice pieces used
    lResultsWithPieces = ContestResult.objects.filter(contest_event__contest=lContest).filter(test_piece__isnull=False).select_related('band', 'contest_event', 'contest_event__contest', 'test_piece').order_by('contest_event__date_of_event')
    if len(lResultsWithPieces) > 0:
        lShowTabs = True
        
    # Hat Tricks at this contest
    lWinRuns = ContestAchievementAward.objects.filter(award="run", contest=lContest)
    if len(lWinRuns) > 0:
        lShowTabs = True
        
    # Find programme covers for contest
    lProgrammeCoverIds = []
    lProgrammeCovers = ContestProgrammeCover.objects.filter(id__in=lProgrammeCoverIds)
    if len(lProgrammeCovers) > 0:
        lShowTabs = True
               
    lContestQualifiesFrom = Contest.objects.filter(qualifies_for=lContest)
    
    lPreviousContestSection = None
    lNextContestSection = None
    if lContest.group:
        try:
            lPreviousContestSection = Contest.objects.filter(group=lContest.group, ordering__lt=lContest.ordering).order_by('-ordering')[0]
        except IndexError:
            lPreviousContestSection = None
                
        try:
            lNextContestSection = Contest.objects.filter(group=lContest.group, ordering__gt=lContest.ordering).order_by('ordering')[0]
        except IndexError:
            lNextContestSection = None
            
    return render_auth(request, 'contests/contest.html', {"Contest" : lContest,
                                                          "Events" : lEvents,
                                                          "FutureEvents" : lFutureEvents,
                                                          "OwnChoicePieceResults" : lResultsWithPieces,
                                                          "WinRuns" : lWinRuns,
                                                          "ShowTabs" : lShowTabs,
                                                          "ProgrammeCovers" : lProgrammeCovers,
                                                          "ContestQualifiesFrom" : lContestQualifiesFrom,
                                                          "PreviousContestSection" : lPreviousContestSection,
                                                          "NextContestSection" : lNextContestSection,
                                                          })

def single_contest_group(request, pGroupSlugUpper):
    try:
        lContestGroup = ContestGroup.objects.filter(slug=pGroupSlugUpper.lower())[0]
    except IndexError:
        raise Http404()
    lContests = lContestGroup.contest_set.exclude(extinct=True).order_by('ordering', 'name')
    lExtinctContests = lContestGroup.contest_set.filter(extinct=True).order_by('ordering', 'name')
    
    if lContestGroup.group_type == "W":
        lTemplate = 'contests/contest_group_whitfriday.html'
    else:
        lTemplate = 'contests/contest_group.html'
    
    lContestEvents = ContestEvent.objects.filter(contest__group=lContestGroup)
    lYears = {}
    for event in lContestEvents:
        try:
            lExistingCount = lYears[event.date_of_event.year]
            lExistingCount += 1 
            lYears[event.date_of_event.year] = lExistingCount
        except KeyError:
            lYears[event.date_of_event.year] = 1
            
    # Fetch programme covers for group
    lProgrammeCovers = ContestProgrammeCover.objects.filter(contest_group=lContestGroup)
    
    lContestGroupAliases = ContestGroupAlias.objects.filter(group=lContestGroup).exclude()
    
    return render_auth(request, lTemplate, {'ContestGroup' : lContestGroup,
                                            'GroupAliases' : lContestGroupAliases,
                                            'Contests' : lContests,
                                            'ExtinctContests' : lExtinctContests,
                                            'Years' : lYears,
                                            'ProgrammeCovers' : lProgrammeCovers,
                                            })
    
    
def single_contest_group_year(request, pGroupSlugUpper, pYear):
    """
    Show contests for a given year for a given group
    """    
    try:
        lContestGroup = ContestGroup.objects.filter(slug=pGroupSlugUpper.lower()).select_related()[0]
    except IndexError:
        raise Http404()
    
    lFirstDay = datetime.datetime(int(pYear), 1, 1)
    lLastDay = datetime.datetime(int(pYear), 12, 31)
    lEvents = ContestEvent.objects.filter(contest__group=lContestGroup, date_of_event__lte=lLastDay, date_of_event__gte=lFirstDay).order_by('contest__ordering').select_related()
    
    try:
        lPreviousEvent = ContestEvent.objects.filter(contest__group=lContestGroup, date_of_event__lt=lFirstDay).order_by('-date_of_event')[0]
    except IndexError:
        lPreviousEvent = None
        
    try:
        lNextEvent = ContestEvent.objects.filter(contest__group=lContestGroup, date_of_event__gt=lLastDay).order_by('date_of_event')[0]
    except IndexError:
        lNextEvent = None
    
    return render_auth(request, "contests/contest_group_year.html", {'ContestGroup' : lContestGroup,
                                                                     'Year' : lLastDay.year,
                                                                     'Events' : lEvents,
                                                                     'NextEvent' : lNextEvent,
                                                                     'PreviousEvent' : lPreviousEvent,
                                                                     })
    
def group_results(request, pGroupSlugUpper, pDate):
    """
    Show overall results for a group 
    """
    try:
        lContestGroup = ContestGroup.objects.filter(slug=pGroupSlugUpper.lower())[0]
        lEvent = ContestEvent.objects.filter(contest__group=lContestGroup)[0]
    except IndexError:
        raise Http404()
    lYear, lMonth, lDay = pDate.split('-')
    lDate = datetime.date(year=int(lYear), month=int(lMonth), day=int(lDay))
    lResults = lContestGroup.group_results(lDate.year)
    return render_auth(request, 'contests/group_results.html', {'ContestGroup' : lContestGroup,
                                                                'Results' : lResults,
                                                                'ContestDate' : lDate})
    
def _add_form_guide_data(pContestEvent, pResults):
    """
    Add form guide for this contest to band details.  Last 10 years results at this event, other results in the last twelve months
    """
    # get hold of a list of bands in contest, excluding those withdrawn or disqualified
    lBandsInContest = []
    for result in pResults:
        if result.results_position_display != 'W' and result.results_position_display != 'D':
            lBandsInContest.append((result.results_position, result.band.name, result.band))
    lBandsInContest.sort()
            
    # Work out contest name without section
    pContestEvent.short_name = pContestEvent.contest.name
    if pContestEvent.contest.group != None:
        lBracketPosition = pContestEvent.contest.name.find('(')  
        if lBracketPosition > 0:
            pContestEvent.short_name = pContestEvent.contest.name[:lBracketPosition]
        else:
            pContestEvent.short_name = pContestEvent.contest.name
        
    lToday = pContestEvent.date_of_event
    lElevenYearsAgo = lToday - datetime.timedelta(days=(11 * 365))
    lOneYearAgo = lToday - datetime.timedelta(days=(1 * 365))
    lBands = []
    lBandIds = []
    for lPosition, lName, lBand in lBandsInContest:
        lBands.append(lBand)
        lBandIds.append(lBand.id)
        for result in pResults:
            if result.band == lBand:
                lBand.conductor = result.person_conducting
                lBand.band_name = result.band_name
        
    # ten years history in this contest
    lRootContestResults = ContestResult.objects.filter(contest_event__date_of_event__lt=pContestEvent.date_of_event)
    if pContestEvent.contest.group_id:
        lRootThisContestResults = lRootContestResults.filter(contest_event__contest__group__id=pContestEvent.contest.group_id)
        lRootOtherContestResults = lRootContestResults.exclude(contest_event__contest__group__id=pContestEvent.contest.group_id)
    else:
        lRootThisContestResults = lRootContestResults.filter(contest_event__contest__slug=pContestEvent.contest.slug)
        lRootOtherContestResults = lRootContestResults.exclude(contest_event__contest__slug=pContestEvent.contest.slug)
            
    lThisContestResultsAllTime = lRootThisContestResults.filter(band__id__in=lBandIds).select_related('band','person_conducting', 'contest_event', 'contest_event__contest','test_piece','contest_event__test_piece')
    lThisContestResultsTenYears = lThisContestResultsAllTime.filter(contest_event__date_of_event__gt=lElevenYearsAgo)
    
    if pContestEvent.contest.group:
        lAllAppearances = ContestResult.objects.filter(contest_event__date_of_event__lt=pContestEvent.date_of_event).filter(band__id__in=lBandIds, contest_event__contest__group__id=pContestEvent.contest.group.id).order_by('contest_event__date_of_event').select_related('contest_event', 'contest_event__contest')
    else:
        lAllAppearances = ContestResult.objects.filter(contest_event__date_of_event__lt=pContestEvent.date_of_event).filter(band__id__in=lBandIds, contest_event__contest__id=pContestEvent.contest.id).order_by('contest_event__date_of_event').select_related('contest_event', 'contest_event__contest')
    
        
    # other results in the last twelve months
    lOtherContestResults = lRootOtherContestResults.filter(contest_event__date_of_event__lt=pContestEvent.date_of_event)
    lOtherContestResults = lOtherContestResults.filter(contest_event__date_of_event__gt=lOneYearAgo)
    lOtherContestResults = lOtherContestResults.exclude(contest_event__contest__group__group_type='W')
    lOtherContestResults = lOtherContestResults.filter(band__id__in=lBandIds).select_related('band','person_conducting', 'contest_event', 'contest_event__contest', 'test_piece', 'contest_event__test_piece')
    
    for lBand in lBands:
        lBand.debut_appearance = None
        lBand.this_contest_history = []
        for result in lThisContestResultsTenYears:
            if result.band_id == lBand.id:
                lBand.this_contest_history.append(result)
        for result in lBand.this_contest_history:
            if pContestEvent.contest.group != None:
                lContestNameLessBracket = result.contest_event.contest.name 
                if lContestNameLessBracket.find('(') > 0:
                    lContestNameLessBracket = lContestNameLessBracket[lContestNameLessBracket.find('('):]
                if lContestNameLessBracket != pContestEvent.contest.name and pContestEvent.contest.name != result.contest_event.contest.name:
                    result.short_name = lContestNameLessBracket
        lBand.other_contest_history = []
        for result in lOtherContestResults:
            if result.band_id == lBand.id:
                lBand.other_contest_history.append(result)
        
        # Number of appearances at this contest
        lBand.appearances_this_contest = 0
        lBand.debut_appearance = None
        for appearance in lAllAppearances:
            if appearance.band_id == lBand.id:
                lBand.appearances_this_contest += 1
                if lBand.debut_appearance == None:
                    lBand.debut_appearance = appearance
                else:
                    if appearance.contest_event.date_of_event < lBand.debut_appearance.contest_event.date_of_event:
                        lBand.debut_apperance = appearance
            
    return lBands
 
    
def _fetch_programme_images(pContestEvent):
    """
    Fetch images for programme cover and pages
    """
    lProgrammeCover = None
    lProgrammePages = None
    lDaysTolerance = 4
    lFewDaysAgo = pContestEvent.date_of_event - datetime.timedelta(days=lDaysTolerance)
    lFewDaysInFuture = pContestEvent.date_of_event + datetime.timedelta(days=lDaysTolerance)
    lContestProgrammeCovers = ContestProgrammeCover.objects.filter(event_date__gt=lFewDaysAgo, event_date__lt=lFewDaysInFuture)
    try:
        lProgrammeCover = lContestProgrammeCovers.filter(contest=pContestEvent.contest)[0]
    except IndexError:
        if pContestEvent.contest.group:
            try:
                # look on contest group
                lProgrammeCover = lContestProgrammeCovers.filter(contest_group=pContestEvent.contest.group)[0]
            except IndexError:
                pass
    if lProgrammeCover:
        lProgrammePages = ContestProgrammePage.objects.filter(cover=lProgrammeCover).order_by('number')

    return lProgrammeCover, lProgrammePages

    
def single_contest_event(request, pContestSlug, pDate):
    """
    Show a single contest event
    """
    try:
        lContestEvent = ContestEvent.objects.filter(contest__slug=pContestSlug, date_of_event=pDate).select_related('contest','contest_type_override_link','venue_link')[0]
    except IndexError:
        # can't find it, try a day either way before returning a 404
        lDate = datetime.datetime.strptime(pDate, '%Y-%m-%d')
        lDateMax = lDate + datetime.timedelta(days=1)
        lDateMin = lDate - datetime.timedelta(days=1)
        try:
            lContestEvent = ContestEvent.objects.filter(contest__slug=pContestSlug, date_of_event__gte=lDateMin, date_of_event__lte=lDateMax)[0]
            return HttpResponsePermanentRedirect('/contests/%s/%s/' % (pContestSlug, lContestEvent.date_of_event))
        except IndexError:
            # can't find it a day either way, try the whole year
            lYear = pDate[:pDate.find('-')]
            lDateMin = '%s-01-01' % lYear
            lDateMax = '%s-12-31' % lYear
            try:
                lContestEvent = ContestEvent.objects.filter(contest__slug=pContestSlug, date_of_event__gte=lDateMin, date_of_event__lte=lDateMax)[0]
                return HttpResponsePermanentRedirect('/contests/%s/%s/' % (pContestSlug, lContestEvent.date_of_event))
            except IndexError:
                raise Http404("No event this date")
    except ValidationError:
        raise Http404("Validation error")
    lContest = lContestEvent.contest
    lResults = lContestEvent.contestresult_set.all().select_related('band','person_conducting','owner', 'band__region', 'test_piece')
    for result in lResults:
        result.extra_pieces = []
        
    lHasOwnChoice = False
    
    lExtraResultPieces = ResultPiecePerformance.objects.filter(result__in=lResults).order_by('result', 'ordering')
    for extra_piece in lExtraResultPieces:
        for result in lResults:
            if extra_piece.result.id == result.id:
                result.extra_pieces.append(extra_piece)
                lHasOwnChoice = True
    
    lPositions = list(range(1, len(lResults)+1 ))  
    lShowPenaltyPoints = False
    lHasMissingPlacings = False
    lHasMissingDraw = False
    lShowPointsFirstPart = False
    lShowPointsSecondPart = False
    lShowPointsThirdPart = False
    lShowPointsFourthPart = False
    lShowPoints = False
    lShowDraw = False
    lShowSecondDraw = False
    lFlags = {}
    lRegionMatch = False
    for result in lResults:
        if result.band.region:
            lFlags[result.band.region.country_code] = result.band.region.country_code
            if request.user.is_anonymous() == False and request.user.profile.is_regional_superuser_region(result.band.region):
                lRegionMatch = True
        if result.test_piece:
            lHasOwnChoice = True
        if result.penalty_points and lContestEvent.contest_type.penalty_points:
            lShowPenaltyPoints = True
        if result.points_first_part and lContestEvent.contest_type.points_one:
            lShowPointsFirstPart = True
        if result.points_second_part and lContestEvent.contest_type.points_two:
            lShowPointsSecondPart = True
        if result.points_third_part and lContestEvent.contest_type.points_three:
            lShowPointsThirdPart = True
        if result.points_fourth_part and lContestEvent.contest_type.points_four:
            lShowPointsFourthPart = True
        if result.points and lContestEvent.contest_type.total_points:
            lShowPoints = True
        if result.draw and lContestEvent.contest_type.first_draw:
            lShowDraw = True
        if result.draw_second_part and lContestEvent.contest_type.second_draw:
            lShowSecondDraw = True
        if result.results_position == None or result.results_position == 0 or result.results_position == 9999:
            lHasMissingPlacings = True
        if result.draw == None or result.draw == 0:
            lHasMissingDraw = True
        if request.user.username == lContestEvent.owner.username:
            # this contest is owned by the current user - change permissions on results to match that user
            if result.owner != request.user:
                if not result.original_owner:
                    result.original_owner = result.owner
                result.owner = request.user
                result.lastChangedBy = request.user
                result.save()
#        if result.draw:
#            lPositions.remove(result.draw)
            
                
    lAdjudicators = ContestAdjudicator.objects.filter(contest_event=lContestEvent).select_related('person')
    
    lPreviousContestEvent = None
    lNextContestEvent = None
    if lContest.group:
        lYear, lMonth, lDay = pDate.split('-')
        lStartOfYear = datetime.date(int(lYear), 1, 1)
        lEndOfYear = datetime.date(int(lYear), 12, 31)
        lRelatedByContestGroup = ContestEvent.objects.filter(contest__group=lContest.group, date_of_event__gte=lStartOfYear, date_of_event__lte=lEndOfYear).select_related('contest')
        try:
            lPreviousContestEvent = lRelatedByContestGroup.filter(contest__ordering__lt=lContest.ordering).order_by('-contest__ordering')[0]
        except IndexError:
            lPreviousContestEvent = None
            
        try:
            lNextContestEvent = lRelatedByContestGroup.filter(contest__ordering__gt=lContest.ordering).order_by('contest__ordering')[0]
        except IndexError:
            lNextContestEvent = None
            
    lContestEventNext = lContestEvent.next
    lContestEventPrevious = lContestEvent.previous
    
    # Take ownership/edit enabled
    lTakeOwnershipEnabled = False
    lShowEdit = False
    if request.user.is_anonymous() == False:
        lTakeOwnershipEnabled = request.user.profile.superuser
        if request.user.profile.enhanced_functionality and lContestEvent.owner.is_superuser:
            lTakeOwnershipEnabled = True
            
        lSuperuser = request.user.profile.superuser
        lEventOwner = lContestEvent.owner.id == request.user.id
        lRegionalSuperuser = (lRegionMatch and request.user.profile.regional_superuser)
        lShowEdit = lSuperuser or lEventOwner or lRegionalSuperuser
        
    # get hold of programme images    
    lProgrammeCover, lProgrammePages = _fetch_programme_images(lContestEvent)
            
    # Find extra test pieces
    lContestTestPieces = ContestTestPiece.objects.filter(contest_event = lContestEvent).select_related('test_piece__composer', 'test_piece__arranger')
    
    lContestEventLinks = ContestEventWeblink.objects.filter(contest_event=lContestEvent)
    
    lStatistics = None
    if lContestEvent.contest_type.statistics:
        lStatistics = _build_contest_statistics(lResults, lContestEvent.contest_type)
        
    lSuperuser = False
    if request.user.is_anonymous() == False:
        lSuperuser = request.user.profile.superuser or (lRegionMatch and request.user.profile.regional_superuser)
        
    lTemplate = 'contests/contest_event.html'
    lToday = datetime.date.today();
    if lContestEvent.date_of_event == lToday:
        lTemplate = 'contests/contest_event_today.html'
        if lHasMissingPlacings:
            lContestEvent.complete = False
    elif lContestEvent.date_of_event > lToday:
        lTemplate = 'contests/contest_event_future.html'
            
    return render_auth(request, lTemplate, {"ContestEvent" : lContestEvent,
                                            "Contest" : lContestEvent.contest,
                                            "PreviousSectionEvent" : lPreviousContestEvent,
                                            "NextSectionEvent" : lNextContestEvent,
                                            "Results" : lResults,
                                            "Adjudicators" : lAdjudicators,
                                            "HasOwnChoice" : lHasOwnChoice,
                                            "ContestEventNext" : lContestEventNext,
                                            "ContestEventPrevious" : lContestEventPrevious,
                                            "OwnerId" : lContestEvent.owner.id,
                                            "Owner" : lContestEvent.owner == request.user,
                                            "TakeOwnershipEnabled" : lTakeOwnershipEnabled,
                                            "ShowPenaltyPoints" : lShowPenaltyPoints,
                                            "ShowPointsFirstPart" : lShowPointsFirstPart,
                                            "ShowPointsSecondPart" : lShowPointsSecondPart,
                                            "ShowPointsThirdPart" : lShowPointsThirdPart,
                                            "ShowPointsFourthPart" : lShowPointsFourthPart,
                                            "ShowPoints" : lShowPoints,
                                            "ShowDraw" : lShowDraw,
                                            "ShowSecondDraw" : lShowSecondDraw,
                                            "ShowEdit" : lShowEdit,
                                            "ContestProgrammeCover" : lProgrammeCover,
                                            "ContestProgrammePages" : lProgrammePages,
                                            "ExtraTestPieces" : lContestTestPieces,
                                            "EventLinks" : lContestEventLinks,
                                            "Statistics" : lStatistics,
                                            "Superuser" : lSuperuser,
                                            "ResultCount" : len(lResults),
                                            "HasMissingDraw" : lHasMissingDraw,
                                            "HasMissingPlacings" : lHasMissingPlacings,
                                            "Positions" : lPositions,
                                            })
    
@login_required
@csrf_exempt
def stars(request, pContestSlug, pDate):
    """
    Star rating done for a contest performance
    """  
    return HttpResponseRedirect("/contests/%s/%s" % (pContestSlug, pDate))
    
@login_required
def autodraw(request, pContestSlug, pDate, pBandSlug, pDrawNumber):
    """
    Assign the passed draw number to the passed band, then redirect band to contest page
    """
    try:
        lContestEvent = ContestEvent.objects.filter(contest__slug=pContestSlug, date_of_event=pDate).select_related('contest','contest_type', 'venue_link')[0]
    except IndexError:
        raise Http404
    
    try:
        lResult = ContestResult.objects.filter(contest_event=lContestEvent, band__slug=pBandSlug)[0]
    except IndexError:
        raise Http404
    
    lResult.draw = pDrawNumber
    lResult.save()
    
    return HttpResponseRedirect('/contests/%s/%s' % (pContestSlug, pDate))
    
    
@login_required_pro_user
def single_contest_event_form_guide(request, pContestSlug, pDate):
    """
    Show a single contest event form guide
    """
    try:
        lContestEvent = ContestEvent.objects.filter(contest__slug=pContestSlug, date_of_event=pDate).select_related('contest')[0]
    except IndexError:
        raise Http404
    lResults = lContestEvent.contestresult_set.all().select_related('band','person_conducting','owner', 'band__region', 'test_piece')
    lFormGuideBands = _add_form_guide_data(lContestEvent, lResults)
    
    lAverageDistanceMi = None
    lAverageDistanceKm = None
    lGeoBands = []
    lBandsToGetDistanceFor = []
    if lContestEvent.venue_link and lContestEvent.venue_link.latitude and lContestEvent.venue_link.longitude:
        for result in lResults:
            if result.results_position != 10001: 
                lBandsToGetDistanceFor.append(result.band.id)
        lGeoBands = Band.objects.filter(id__in=lBandsToGetDistanceFor).exclude(latitude__isnull=True, longitude__isnull=True).exclude(latitude='', longitude='').distance(lContestEvent.venue_link.point).order_by('-distance')
        
        lTotalDistanceMi = 0
        lTotalDistanceKm = 0
        lGeoBandCount = len(lGeoBands)
        for band in lGeoBands:
            lTotalDistanceMi += band.distance.mi
            lTotalDistanceKm += band.distance.km
            
        if lGeoBandCount > 0:
            lAverageDistanceMi = lTotalDistanceMi / lGeoBandCount
            lAverageDistanceKm = lTotalDistanceKm / lGeoBandCount 
        
    for geoband in lGeoBands:
        for band in lFormGuideBands:
            if geoband.id == band.id:
                geoband.band_name = band.band_name
                break
        
    return render_auth(request, 'contests/contest_event_form_guide.html', {"ContestEvent" : lContestEvent,
                                                                           "Contest" : lContestEvent.contest,
                                                                           "Results" : lResults,
                                                                           "GeoBands" : lGeoBands,
                                                                           "GeoAverageDistanceMi" : lAverageDistanceMi,
                                                                           "GeoAverageDistanceKm" : lAverageDistanceKm, 
                                                                           "FormGuideBands" : lFormGuideBands,
                                                                })
    

class Statistics(object):
    pass

def _build_contest_statistics(pContestResults, pContestType):
    """
    Build up contest statistics from individual adjudicator results
    """
    import scipy.stats
    lStatistics = Statistics()
    lAdjAResults = []
    lAdjBResults = []
    lAdjCResults = []
    for lResult in pContestResults:
        if lResult.points_first_part: lAdjAResults.append(int(lResult.points_first_part))
        if lResult.points_second_part: lAdjBResults.append(int(lResult.points_second_part))
        if lResult.points_third_part: lAdjCResults.append(int(lResult.points_third_part))
        
    if pContestType.statistics_limit >= 2 and len(lAdjAResults) > 0 and len(lAdjBResults) > 0:
        lStatistics.spearman_a_b = scipy.stats.spearmanr(lAdjAResults, lAdjBResults)[0]
        lStatistics.kendall_a_b = scipy.stats.kendalltau(lAdjAResults, lAdjBResults)[0]
            
        if pContestType.statistics_limit >= 3 and len(lAdjCResults) > 0:        
            lStatistics.spearman_a_c = scipy.stats.spearmanr(lAdjAResults, lAdjCResults)[0]
            lStatistics.spearman_b_c = scipy.stats.spearmanr(lAdjBResults, lAdjCResults)[0]
            
            lStatistics.kendall_a_c = scipy.stats.kendalltau(lAdjAResults, lAdjCResults)[0]
            lStatistics.kendall_b_c = scipy.stats.kendalltau(lAdjBResults, lAdjCResults)[0]
    else:
        lStatistics = None
    
    return lStatistics


@login_required_pro_user
def single_contest_event_competitors(request, pContestSlug, pDate):
    """
    List users that have this contest as part of their performance history
    """
    try:
        lContestEvent = ContestEvent.objects.filter(contest__slug=pContestSlug, date_of_event=pDate).select_related('contest', 'venue_link')[0]
    except IndexError:
        # can't find it, try a day either way before returning a 404
        lDate = datetime.datetime.strptime(pDate, '%Y-%m-%d')
        lDateMax = lDate + datetime.timedelta(days=1)
        lDateMin = lDate - datetime.timedelta(days=1)
        try:
            lContestEvent = ContestEvent.objects.filter(contest__slug=pContestSlug, date_of_event__gte=lDateMin, date_of_event__lte=lDateMax)[0]
            return HttpResponsePermanentRedirect('/contests/%s/%s/' % (pContestSlug, lContestEvent.date_of_event))
        except IndexError:
            # can't find it a day either way, try the whole year
            lYear = pDate[:pDate.find('-')]
            lDateMin = '%s-01-01' % lYear
            lDateMax = '%s-12-31' % lYear
            try:
                lContestEvent = ContestEvent.objects.filter(contest__slug=pContestSlug, date_of_event__gte=lDateMin, date_of_event__lte=lDateMax)[0]
                return HttpResponsePermanentRedirect('/contests/%s/%s/' % (pContestSlug, lContestEvent.date_of_event))
            except IndexError:
                raise Http404("No event this date")
    except ValidationError:
        raise Http404("Validation error")
    lContest = lContestEvent.contest
    lResults = lContestEvent.contestresult_set.all().select_related('band','person_conducting','owner', 'band__region', 'test_piece')
    
    lCompetitors = PersonalContestHistory.objects.filter(result__in=lResults).order_by("result__results_position")
    for competitor in lCompetitors:
        if competitor.user.profile.contest_history_visibility == 'private':
            competitor.display_name = 'private'
        else:
            competitor.display_name = competitor.user.username
        
        
    return render_auth(request, 'contests/contest_event_competitors.html', {"ContestEvent" : lContestEvent,
                                                                            "Contest" : lContestEvent.contest,
                                                                            "Results" : lResults,
                                                                            "Competitors" : lCompetitors,
                                                                           })

    
@login_required_pro_user
def single_contest_event_map(request, pContestSlug, pDate):
    """
    Show a map for a single contest event
    """
    try:
        lContestEvent = ContestEvent.objects.filter(contest__slug=pContestSlug, date_of_event=pDate).select_related('contest', 'venue_link')[0]
    except IndexError:
        # can't find it, try a day either way before returning a 404
        lDate = datetime.datetime.strptime(pDate, '%Y-%m-%d')
        lDateMax = lDate + datetime.timedelta(days=1)
        lDateMin = lDate - datetime.timedelta(days=1)
        try:
            lContestEvent = ContestEvent.objects.filter(contest__slug=pContestSlug, date_of_event__gte=lDateMin, date_of_event__lte=lDateMax)[0]
            return HttpResponsePermanentRedirect('/contests/%s/%s/' % (pContestSlug, lContestEvent.date_of_event))
        except IndexError:
            # can't find it a day either way, try the whole year
            lYear = pDate[:pDate.find('-')]
            lDateMin = '%s-01-01' % lYear
            lDateMax = '%s-12-31' % lYear
            try:
                lContestEvent = ContestEvent.objects.filter(contest__slug=pContestSlug, date_of_event__gte=lDateMin, date_of_event__lte=lDateMax)[0]
                return HttpResponsePermanentRedirect('/contests/%s/%s/' % (pContestSlug, lContestEvent.date_of_event))
            except IndexError:
                raise Http404("No event this date")
    except ValidationError:
        raise Http404("Validation error")
    lContest = lContestEvent.contest
    lResults = lContestEvent.contestresult_set.all().select_related('band','person_conducting','owner', 'band__region', 'test_piece')

    # geography data    
    lAverageDistanceMi = None
    lAverageDistanceKm = None
    lGeoBands = []
    lBandsToGetDistanceFor = []
    if lContestEvent.venue_link and lContestEvent.venue_link.latitude and lContestEvent.venue_link.longitude:
        for result in lResults:
            lBandsToGetDistanceFor.append(result.band.id)
        lGeoBands = Band.objects.filter(id__in=lBandsToGetDistanceFor).exclude(latitude__isnull=True, longitude__isnull=True).exclude(latitude='', longitude='').distance(lContestEvent.venue_link.point).order_by('-distance')
        
        lTotalDistanceMi = 0
        lTotalDistanceKm = 0
        lGeoBandCount = len(lGeoBands)
        for band in lGeoBands:
            if band.distance:
                lTotalDistanceMi += band.distance.mi
                lTotalDistanceKm += band.distance.km
            else:
                lGeoBandCount -= 1 # take one off total - this band doesn't have a location
            
        if lGeoBandCount > 0:
            lAverageDistanceMi = lTotalDistanceMi / lGeoBandCount
            lAverageDistanceKm = lTotalDistanceKm / lGeoBandCount 
        
    lFormGuideBands = _add_form_guide_data(lContestEvent, lResults)
    for geoband in lGeoBands:
        for band in lFormGuideBands:
            if geoband.id == band.id:
                geoband.band_name = band.band_name
                break
            
    if len(lResults) == 0:
        raise Http404
        
    return render_auth(request, 'contests/contest_event_map.html', {"ContestEvent" : lContestEvent,
                                                                    "Contest" : lContestEvent.contest,
                                                                    "Results" : lResults,
                                                                    "GeoBands" : lGeoBands,
                                                                    "GeoAverageDistanceMi" : lAverageDistanceMi,
                                                                    "GeoAverageDistanceKm" : lAverageDistanceKm, 
                                                                    "OwnerId" : lContestEvent.owner.id,
                                                                    "Owner" : lContestEvent.owner == request.user,
                                                                    "FormGuideBands" : lFormGuideBands,
                                                                })


def single_contest_event_programme(request, pContestSlug, pDate):
    """
    Show scanned pages from a contest programme
    """
    try:
        lContestEvent = ContestEvent.objects.filter(contest__slug=pContestSlug, date_of_event=pDate).select_related()[0]
    except IndexError:
        raise Http404()
    except ValidationError:
        raise Http404()

    lProgrammeCover, lProgrammePages = _fetch_programme_images(lContestEvent)
    
    if lProgrammeCover == None:
        raise Http404()
    
    return render_auth(request, 'contests/contest_event_programme.html', {
                                                                    "ContestEvent" : lContestEvent,
                                                                    "Contest" : lContestEvent.contest,
                                                                    "ContestProgrammeCover" : lProgrammeCover,
                                                                    "ContestProgrammePages" : lProgrammePages,
                                                                         })


@login_required  
def edit_result(request, pResultSerial):
    """
    Edit a single result row
    """
    try:
        lContestResult = ContestResult.objects.filter(id=pResultSerial).select_related('contest_event','contest_event__contest','band')[0]
    except IndexError:
        raise Http404
    lContestEvent = lContestResult.contest_event
    lContest = lContestEvent.contest
    
    if request.user.profile.superuser == False and request.user.profile.is_regional_superuser_region(lContestResult.band.region) == False:
        if request.user != lContestEvent.owner:
            raise Http404

    if request.method == 'POST':
        form = ContestResultForm(request.POST, instance=lContestResult)
        if form.is_valid():
            lContestResult = form.save(commit=False)
            lPenaltyPoints = lContestResult.penalty_points
            if lPenaltyPoints and len(lPenaltyPoints.strip()) > 0:
                if lPenaltyPoints.strip().startswith('-') == False:
                    lContestResult.penalty_points = "-%s" % lPenaltyPoints.strip()
            try:
                lNewBandId = request.POST['band_list_id']
                lContestResult.band_id = lNewBandId
            except MultiValueDictKeyError:
                pass # band has not been changed
            
            try:
                lNewConductorId = request.POST['conductor_list_id']
                if lNewConductorId != '':
                    lContestResult.person_conducting_id = lNewConductorId
                    lMatchingPerson = Person.objects.filter(id=lNewConductorId)[0]
            except MultiValueDictKeyError:
                pass # conductor has not been changed
            
            try:
                lNewTestPieceId = request.POST['testpiece_list_id']
                if lNewTestPieceId == '':
                    lNewTestPieceId = None
                lContestResult.test_piece_id = lNewTestPieceId
            except MultiValueDictKeyError:
                pass # test piece has not been changed
            
            lOldResult = ContestResult.objects.filter(id=lContestResult.id)[0]
            lContestResult.lastChangedBy = request.user
            lContestResult.save()
            notification(lOldResult, lContestResult, 'contests', 'contest_result', 'edit', request.user, browser_details(request))
            return HttpResponseRedirect('/contests/%s/%s/' % (lContestResult.contest_event.contest.slug, lContestResult.contest_event.date_of_event))
    else:
        form = ContestResultForm(instance=lContestResult)
        
    # Find extra test pieces
    lContestTestPieces = ContestTestPiece.objects.filter(contest_event = lContestEvent).select_related('test_piece__composer', 'test_piece__arranger')
    # Adjudicators
    lAdjudicators = ContestAdjudicator.objects.filter(contest_event=lContestEvent).select_related('person')

    return render_auth(request, 'contests/edit_result.html', {'form': form, 
                                                              'ContestResult' : lContestResult,
                                                              'Position' : lContestResult.results_position,
                                                              'ContestEvent' : lContestEvent,
                                                              'Contest' : lContest,
                                                              'Adjudicators' : lAdjudicators,
                                                              'ExtraTestPieces' : lContestTestPieces,
                                                              })


@login_required  
def delete_result(request, pResultSerial):
    """
    Delete a single result row
    """
    lContestResult = get_object_or_404(ContestResult, pk=pResultSerial)
    
    lAllowedToDelete = False
    if request.user.profile.superuser:
        lAllowedToDelete = True
    if request.user.profile.is_regional_superuser_region(lContestResult.band.region):
        lAllowedToDelete = True
    if request.user == lContestResult.owner and request.user.profile.enhanced_functionality:
        lAllowedToDelete = True
            
    if lAllowedToDelete == False:
        raise Http404()
    
    notification(None, lContestResult, 'contests', 'contest_result', 'delete', request.user, browser_details(request))
    lContestResult.delete()
    
    return HttpResponseRedirect('/contests/%s/%s/' % (lContestResult.contest_event.contest.slug, lContestResult.contest_event.date_of_event))


@login_required  
def edit_contest(request, pContestSlug):
    """
    Edit a contest 
    """
    if request.user.profile.superuser == False:
        raise Http404()
    
    try:
        lContest = Contest.objects.filter(slug=pContestSlug)[0]
    except IndexError:
        raise Http404
    
    if request.method == 'POST':
        lOriginalContest = Contest.objects.filter(id=lContest.id)[0]
        form = ContestForm(request.POST, instance=lContest)
        if form.is_valid():
            lContestToSave = form.save(commit=False)
            lContestToSave.lastChangedBy = request.user
            
            notification(lOriginalContest, lContestToSave, 'contests', 'contest', 'edit', request.user, browser_details(request))
            
            lContestToSave.save()
            return HttpResponseRedirect('/contests/%s/' % lContest.slug)
    else:
        form = ContestForm(instance=lContest)

    return render_auth(request, 'contests/edit_contest.html', {'form': form, 'Contest' : lContest})


@login_required
def delete_contest(request, pContestSlug):
    """
    Delete a contest that has no events
    """
    if request.user.profile.superuser == False:
        raise Http404()
    
    try:
        lContest = Contest.objects.filter(slug=pContestSlug)[0]
    except IndexError:
        raise Http404
    
    if lContest.count > 0:
        raise Http404
    
    lContest.delete()
    notification(lContest, None, 'contests', 'contest', 'delete', request.user, browser_details(request))

    return HttpResponseRedirect('/contests/')


@login_required  
def edit_event(request, pContestSlug, pContestDate, pEventSerial):
    """
    Edit a contest event
    """
    try:
        lContestEvent = ContestEvent.objects.filter(id=pEventSerial)[0]
    except IndexError:
        raise Http404
    
    lSuperuser = request.user.profile.superuser
    lRegionalSuperuser = request.user.profile.regional_superuser
    lOwner = request.user == lContestEvent.owner
    
    if (lSuperuser or lRegionalSuperuser or lOwner) == False:
        raise Http404
    
    if request.method == 'POST':
        form = ContestEventForm(request.POST, instance=lContestEvent)
        if form.is_valid():
            lOldEvent = ContestEvent.objects.filter(id=lContestEvent.id)[0]
            
            lNewEvent = form.save(commit=False)
            lNewEvent.lastChangedBy = request.user
            lNewEvent.save()
            
            notification(lOldEvent, lNewEvent, 'contests', 'contestevent', 'edit', request.user, browser_details(request))
                        
            return HttpResponseRedirect("/contests/%s/%s" % (lContestEvent.contest.slug, lContestEvent.date_of_event))
    else:
        form = ContestEventForm(instance=lContestEvent)

    return render_auth(request, 'contests/edit_contest_event.html', {'form': form, 'ContestEvent' : lContestEvent})


@login_required
def add_to_contest_history(request, pContestSlug, pDate):
    """
    Add this contest to the user's personal contest historysingle_contest_event
    """
    try:
        lContestEvent = ContestEvent.objects.filter(contest__slug=pContestSlug, date_of_event=pDate).select_related()[0]
    except IndexError:
        raise Http404()
    except ValidationError:
        raise Http404()
    
    lPlayerPositions = PlayerPosition.objects.all()
    return render_auth(request, 'contests/add_to_contest_history.html', {'PlayerPositions' : lPlayerPositions,
                                                                         'ContestEvent' : lContestEvent
                                                                         })


@login_required
def take_ownership(request, pContestSlug, pDate):
    """
    Take over ownership of this contest result
    """
    try:
        lContestEvent = ContestEvent.objects.filter(contest__slug=pContestSlug, date_of_event=pDate).select_related()[0]
        lExistingOwner = lContestEvent.owner
        if not lContestEvent.original_owner:
            lContestEvent.original_owner = lExistingOwner
        lContestEvent.owner = request.user
        lContestEvent.lastChangedBy = request.user
        lContestEvent.save()
        for result in lContestEvent.contestresult_set.all():
            result.owner = request.user
            result.save()
    except IndexError:
        raise Http404()
    except ValidationError:
        raise Http404()
    
    notification(lExistingOwner, lContestEvent, 'contests', 'contestevent', 'take_ownership', request.user, browser_details(request))
    
    return HttpResponseRedirect('/contests/%s/%s/' % (lContestEvent.contest.slug, lContestEvent.date_of_event))


@login_required
def add_result_to_contest_history(request, pContestSlug, pDate, pResultSerial):
    """
    Add a specific result to this user's personal contest history, then redirect to their list on the profile
    """
    try:
        lContestResult = ContestResult.objects.filter(id=pResultSerial)[0]
    except IndexError:
        raise Http404()
    lCheckForExisting = PersonalContestHistory.objects.filter(result=lContestResult, user=request.user).count()
    if lCheckForExisting == 0:
        lPlayerPositionSerial = request.GET.get('position')
        try:
            lPlayerPosition = PlayerPosition.objects.filter(id=lPlayerPositionSerial)[0]
        except:
            lPlayerPosition = None
        
        lContestHistory = PersonalContestHistory()
        lContestHistory.user = request.user
        lContestHistory.result = lContestResult
        lContestHistory.instrument = lPlayerPosition
        lContestHistory.save()

        notification(None, lContestHistory, 'contests', 'performances', 'new', request.user, browser_details(request))

    if lCheckForExisting > 0:
        lExisting = PersonalContestHistory.objects.filter(result=lContestResult, user=request.user)[0]
        if lExisting.status == 'pending':
            lExisting.status = 'accepted'
            lExisting.save()

            notification(None, lContestHistory, 'contests', 'performances', 'accept', request.user, browser_details(request))
        
    lPath = '/users/%s/contest_history/' % request.user.username
    return HttpResponseRedirect(lPath)

@login_required
def add_future_event(request, pContestSlug):
    """
    Add a future event for a contest
    """
    try:
        lContest = Contest.objects.filter(slug=pContestSlug)[0]
    except IndexError:
        raise Http404()
    
    
    if request.method == 'POST':
        lForm = FutureEventForm(request.POST)
        if lForm.is_valid():
            lContestEvent = lForm.save(commit=False)
            lContestEvent.contest = lContest
            lContestEvent.name = lContest.name
            lContestEvent.owner = request.user
            lContestEvent.lastChangedBy = request.user
            lContestEvent.save()
            notification(None, lContestEvent, 'contests', 'future_event', 'new', request.user, browser_details(request))
            return HttpResponseRedirect('/contests/%s/' % lContest.slug)
    else:
        try:
            lLatestContestEvent = ContestEvent.objects.filter(contest=lContest).order_by('-date_of_event')[0]
        except IndexError:
            lLatestContestEvent = ContestEvent()
        
        lContestEvent = ContestEvent()
        lContestEvent.venue_link = lLatestContestEvent.venue_link

        lForm = FutureEventForm(instance=lContestEvent)
    
    
    return render_auth(request, 'contests/add_future_event.html', {'Contest' : lContest,
                                                                   'form' : lForm})
    
@login_required
def delete_future_event(request, pContestSlug, pEventId):
    """
    Delete a future event
    """
    try:
        lContest = Contest.objects.filter(slug=pContestSlug)[0]
        lEvent = ContestEvent.objects.filter(id=pEventId)[0]
    except IndexError:
        raise Http404()
    
    if request.user == lEvent.owner:
        notification(None, lEvent, 'contests', 'future_event', 'delete', request.user, browser_details(request))
        lEvent.delete()
        
    return HttpResponseRedirect('/contests/%s/' % lContest.slug)


@login_required
def add_future_event_popup(request):
    """
    Show a popup to allow a future event to be added
    """
    if request.method == 'POST':
        lForm = FutureEventFormNoContest(request.POST)
        if lForm.is_valid():
            lContestEvent = lForm.save(commit=False)
            lContestEvent.owner = request.user
            lContestEvent.lastChangedBy = request.user
            lContestEvent.save()
            notification(None, lContestEvent, 'contests', 'future_event', 'new', request.user, browser_details(request))
            return HttpResponseRedirect('/')

    lForm = FutureEventFormNoContest()
    return render_auth(request, 'contests/AddFutureEvent.htm', {'form' : lForm});

    
def _handle_uploaded_file(request, pProgrammeCover):
    """
    Write the uploaded file to disk
    """
    lFileContents = ContentFile(request.FILES['image'].read())
    pProgrammeCover.image.save(request.FILES['image'].name, lFileContents)
    
    
@login_required
def upload_programme_cover(request):
    """
    Allow upload of contest programme cover image
    """
    if request.user.profile.enhanced_functionality == False:
        raise Http404
    
    if request.method == 'POST':
        lForm = ContestProgrammeCoverForm(request.POST, request.FILES)
        if lForm.is_valid():
            lProgrammeCover = lForm.save(commit=False)
            lProgrammeCover.owner = request.user
            lProgrammeCover.lastChangedBy = request.user
            _handle_uploaded_file(request, lProgrammeCover)
            lProgrammeCover.save()
            notification(None, lProgrammeCover, 'contests', 'programme_cover', 'new', request.user, browser_details(request))
            
            if lProgrammeCover.contest_group:
                lRedirectUrl = '/contests/%s/%s/' % (lProgrammeCover.contest_group.actual_slug, lProgrammeCover.event_date.year)
            else:
                lRedirectUrl = '/contests/%s/%s/' % (lProgrammeCover.contest.slug, lProgrammeCover.event_date)
            
            return HttpResponseRedirect(lRedirectUrl)
    else:
        lForm = ContestProgrammeCoverForm()
    
    return render_auth(request, 'contests/upload_programme_cover.html', {'form' : lForm})

@login_required
def assign_position_from_points(request, pContestSlug, pContestDate):
    """
    Assign any blank positions from the points on the contest results
    """
    if request.user.profile.superuser == False:
        raise Http404
    try:
        lContestEvent = ContestEvent.objects.filter(contest__slug=pContestSlug, date_of_event=pContestDate)[0]
    except IndexError:
        raise Http404
    
    lResults = ContestResult.objects.filter(contest_event=lContestEvent)
    lResultStructure = []
    for result in lResults:
        if result.points:
            lResultStructure.append((float(result.points), result.id, result.results_position))
        
    lPositionAwarded = 0
    lLastPoints = 0
    lJump = 1
    lResultStructure.sort()
    lResultStructure.reverse()
    for row in lResultStructure:
        lPoints = row[0]
        lResultId = row[1]
        lPosition = row[2]

        if lLastPoints != lPoints:
            lPositionAwarded += lJump
            lJump = 1
        else:
            # tied position, leave lPositionAwarded as is, but jump more later
            lJump += 1
        
        if lPosition == 9999:
            lResult = ContestResult.objects.filter(id=lResultId, contest_event=lContestEvent)[0]
            lResult.results_position = lPositionAwarded
            lResult.save()

        lLastPoints = lPoints
        
    return HttpResponseRedirect('/contests/%s/%s/' % (pContestSlug, pContestDate))
    
    
def _merge_result(pResultWithPosition, pResultWithoutPosition):
    """
    Merge missing details from one result to the other
    """
    if pResultWithPosition.band_id != pResultWithoutPosition.band_id:
        raise Http404("Attempt to merge results where two results have different bands attached")
    
    if pResultWithPosition.person_conducting_id == settings.UNKNOWN_PERSON_ID and pResultWithoutPosition.person_conducting_id != settings.UNKNOWN_PERSON_ID: # unknown
        pResultWithPosition.person_conducting_id = pResultWithoutPosition.person_conducting_id
        
    if pResultWithPosition.draw == 0 and pResultWithoutPosition.draw != 0:
        pResultWithPosition.draw = pResultWithoutPosition.draw
    if pResultWithPosition.draw_second_part == 0 and pResultWithoutPosition.draw_second_part != 0: 
        pResultWithPosition.draw_second_part = pResultWithoutPosition.draw_second_part
        
    if pResultWithPosition.points == None and pResultWithoutPosition.points != None or pResultWithPosition.points == '0' and pResultWithoutPosition.points != None:
        pResultWithPosition.points = pResultWithoutPosition.points  
    if pResultWithPosition.points_first_part == None and pResultWithoutPosition.points_first_part != None or pResultWithPosition.points_first_part == '0' and pResultWithoutPosition.points_first_part != None:
        pResultWithPosition.points_first_part = pResultWithoutPosition.points_first_part   
    if pResultWithPosition.points_second_part == None and pResultWithoutPosition.points_second_part != None or pResultWithPosition.points_second_part == '0' and pResultWithoutPosition.points_second_part != None:
        pResultWithPosition.points_second_part = pResultWithoutPosition.points_second_part   
    if pResultWithPosition.points_third_part == None and pResultWithoutPosition.points_third_part != None or pResultWithPosition.points_third_part == '0' and pResultWithoutPosition.points_third_part != None:
        pResultWithPosition.points_third_part = pResultWithoutPosition.points_third_part  
    if pResultWithPosition.points_fourth_part == None and pResultWithoutPosition.points_fourth_part != None or pResultWithPosition.points_fourth_part == '0' and pResultWithoutPosition.points_fourth_part != None:
        pResultWithPosition.points_fourth_part = pResultWithoutPosition.points_fourth_part  
    if pResultWithPosition.penalty_points == None and pResultWithoutPosition.penalty_points != None or pResultWithPosition.penalty_points == '0' and pResultWithoutPosition.penalty_points != None:
        pResultWithPosition.penalty_points = pResultWithoutPosition.penalty_points   
    
    if pResultWithPosition.test_piece_id == None and pResultWithoutPosition.test_piece_id != None:
        pResultWithPosition.test_piece_id = pResultWithoutPosition.test_piece_id        
        
    if pResultWithPosition.notes != pResultWithoutPosition.notes:
        pResultWithPosition.notes += "\n" + pResultWithoutPosition.notes
    
    pResultWithPosition.save()
    pResultWithoutPosition.delete()
    

@login_required
def single_contest_event_compress(request, pContestSlug, pContestDate):
    """
    Look through results for multiple entries for the same band, and copy missing details from the unplaced entry onto the placed entry
    """    
    if request.user.profile.superuser == False:
        raise Http404

    try:
        lContestEvent = ContestEvent.objects.filter(contest__slug=pContestSlug, date_of_event=pContestDate)[0]
    except IndexError:
        raise Http404
    
    lResults = ContestResult.objects.filter(contest_event=lContestEvent).order_by('band')
    
    lPreviousResult = None
    for result in lResults:
        if lPreviousResult != None and lPreviousResult.band_id == result.band_id:
            if lPreviousResult.results_position == 9999 and result.results_position != 9999:
                _merge_result(result, lPreviousResult)
            elif lPreviousResult.results_position != 9999 and result.results_position == 9999:
                _merge_result(lPreviousResult, result)
            elif lPreviousResult.draw != 0 and result.draw == 0:
                _merge_result(lPreviousResult, result)
            elif lPreviousResult.draw == 0 and result.draw != 0:
                _merge_result(result, lPreviousResult)
                
        lPreviousResult = result
                    
    return HttpResponseRedirect('/contests/%s/%s/' % (pContestSlug, pContestDate))    

@login_required
def single_contest_event_propagate_march(request, pContestSlug, pContestDate):
    """
    Find other results for the same band on the same date, and copy the test piece from results for this contest onto those results
    """    
    if request.user.profile.superuser == False:
        raise Http404

    try:
        lContestEvent = ContestEvent.objects.filter(contest__slug=pContestSlug, date_of_event=pContestDate)[0]
    except IndexError:
        raise Http404
    
    lThisContestResults = ContestResult.objects.filter(contest_event=lContestEvent).order_by('band')
    
    lOtherContestsSameDate = ContestEvent.objects.filter(date_of_event=pContestDate)
    if lOtherContestsSameDate.count() > 0:
        for result in lThisContestResults:
            if result.test_piece:
                lBand = result.band
                for otherContestEvent in lOtherContestsSameDate:
                    try:
                        lOtherContestResult = ContestResult.objects.filter(contest_event=otherContestEvent, band=lBand)[0]
                        if lOtherContestResult.test_piece == None:
                            lOtherContestResult.test_piece = result.test_piece
                            lOtherContestResult.save()
                    except IndexError:
                        pass
                    
    return HttpResponseRedirect('/contests/%s/%s/' % (pContestSlug, pContestDate))    

@login_required
def contest_groups(request):
    """
    Show list of contest groups, and allow the ones with no contests to be deleted
    """
    if request.user.profile.superuser == False:
        raise Http404
    
    if request.method == 'POST':
        lNewGroup = ContestGroup()
        lNewGroup.name = request.POST['groupname'].strip()
        if len(lNewGroup.name) > 0: 
            lNewGroup.slug = slugify(lNewGroup.name)
            lNewGroup.type = 'S'
            lNewGroup.lastChangedBy = request.user
            lNewGroup.owner = request.user
            lNewGroup.save()
        return HttpResponseRedirect('/contests/groups/')
    
    cursor = connection.cursor()
    lGroups = {}
    
    cursor.execute("SELECT g.id, g.name, g.slug, c.name, c.slug FROM contests_contestgroup g LEFT OUTER JOIN contests_contest c ON c.group_id = g.id")
    
    rows = cursor.fetchall()
    for row in rows:
        lGroupSlug = row[2]
        try:
            lGroup = lGroups[lGroupSlug]
            if row[3] and len(row[3]) > 0:
                lGroup['contests'].append((row[3],row[4],))
        except KeyError:
            lGroup = {
                      'id' : row[0],
                      'name' : row[1],
                      'slug' : row[2],
                      'contests': [],
                      'aliases': [],
                      }
            if row[3]:
                lGroup['contests'].append((row[3],row[4],))
            lGroups[lGroupSlug] = lGroup
    cursor.close()
    
    from operator import itemgetter
    lGroupsToShow = sorted(lGroups.values(), key=itemgetter('name'))
    
    lContestGroupAliases = ContestGroupAlias.objects.all()
     
    for group in lGroupsToShow:
        group['count'] = len(group['contests'])
        for alias in lContestGroupAliases:
            if alias.group_id == group['id']:
                group['aliases'].append(alias.name)
    lGroupsCount = len(lGroupsToShow)
    
    return render_auth(request, 'contests/groups_list.html', {'Groups' : lGroupsToShow,
                                                              'GroupCount' : lGroupsCount,
                                                              })
    
@login_required
def delete_contest_group(request, pContestGroupId):
    """
    Delete a specific contest group
    """
    if request.user.profile.superuser == False:
        raise Http404
    
    try:
        lGroup = ContestGroup.objects.filter(id=pContestGroupId)[0]
    except IndexError:
        raise Http404
    
    lGroup.delete()
    
    return HttpResponseRedirect('/contests/groups/')    


def contest_programmes(request):
    """
    Show contest programmes index
    """
    lProgrammes = ContestProgrammeCover.objects.all().order_by('-event_date').select_related('contest','contest_group')
    
    return render_auth(request, 'contests/programmes_index.html', {
                                                                   'ContestProgrammes': lProgrammes,
                                                                   })
    
@login_required
def talk_contest(request, pSlug):
    """
    Show the talk page for a particular contest
    """
    if request.user.profile.superuser == False:
        raise Http404
   
    try:
        lObjectLink = Contest.objects.filter(slug=pSlug)[0]
    except IndexError:
        raise Http404
    
    try:
        lTalk = ContestTalkPage.objects.filter(object_link=lObjectLink)[0]
    except IndexError:
        lTalk = None
        
    lRecentTalkChanges = fetch_recent_talk_changes(request)       
        
    return render_auth(request, 'talk/talk.html', {
                                                    'Talk' : lTalk,
                                                    'ObjectLink' : lObjectLink,
                                                    'Offset' : 'contests',
                                                    'RecentTalkChanges' : lRecentTalkChanges,
                                                   })
    
@login_required
def talk_edit_contest(request, pSlug):
    """
    Edit the talk page
    """
    if request.user.profile.superuser == False:
        raise Http404
    
    try:
        lObjectLink = Contest.objects.filter(slug=pSlug)[0]
    except IndexError:
        raise Http404
    
    try:
        lTalk = ContestTalkPage.objects.filter(object_link=lObjectLink)[0]
    except IndexError:
        lTalk = ContestTalkPage()
        lTalk.lastChangedBy = request.user
        lTalk.owner = request.user
        lTalk.object_link = lObjectLink
        lTalk.save()
        
    if request.method == "POST":
        form = ContestTalkEditForm(data=request.POST, instance=lTalk)
        if form.is_valid():
            lTalk = form.save(commit=False)
            lTalk.lastChangedBy = request.user
            lTalk.owner = request.user
            lTalk.object_link = lObjectLink
            lTalk.save()

            notification(None, lTalk, 'contest_talk', 'edit', request.user, browser_details(request))

            return HttpResponseRedirect('/contests/%s/talk/' % lObjectLink.actual_slug)
        
    else:
        form = ContestTalkEditForm(instance=lTalk)        
        
    return render_auth(request, 'talk/talk_edit.html', {
                                                    'Talk' : lTalk,
                                                    'ObjectLink' : lObjectLink,
                                                    'Offset' : 'contests',
                                                    'form' : form,
                                                    })        
    
@login_required
def talk_group(request, pSlug):
    """
    Show the talk page for a particular contest group
    """
    if request.user.profile.superuser == False:
        raise Http404
   
    try:
        lObjectLink = ContestGroup.objects.filter(slug=pSlug.lower())[0]
    except IndexError:
        raise Http404
    
    try:
        lTalk = GroupTalkPage.objects.filter(object_link=lObjectLink)[0]
    except IndexError:
        lTalk = None
        
    lRecentTalkChanges = fetch_recent_talk_changes(request)           
        
    return render_auth(request, 'talk/talk.html', {
                                                    'Talk' : lTalk,
                                                    'ObjectLink' : lObjectLink,
                                                    'Offset' : 'contests',
                                                    'RecentTalkChanges' : lRecentTalkChanges,
                                                   })
    
@login_required
def talk_edit_group(request, pSlug):
    """
    Edit the talk page
    """
    if request.user.profile.superuser == False:
        raise Http404
    
    try:
        lObjectLink = ContestGroup.objects.filter(slug=pSlug.lower())[0]
    except IndexError:
        raise Http404
    
    try:
        lTalk = GroupTalkPage.objects.filter(object_link=lObjectLink)[0]
    except IndexError:
        lTalk = GroupTalkPage()
        lTalk.lastChangedBy = request.user
        lTalk.owner = request.user
        lTalk.object_link = lObjectLink
        lTalk.save()
     
    if request.method == "POST":
        form =GroupTalkEditForm(data=request.POST, instance=lTalk)
        if form.is_valid():
            lTalk = form.save(commit=False)
            lTalk.lastChangedBy = request.user
            lTalk.owner = request.user
            lTalk.object_link = lObjectLink
            lTalk.save()

            notification(None, lTalk, 'group_talk', 'edit', request.user, browser_details(request))

            return HttpResponseRedirect('/contests/%s/talk/' % lObjectLink.actual_slug)
        
    else:
        form = GroupTalkEditForm(instance=lTalk) 
        
    return render_auth(request, 'talk/talk_edit.html', {
                                                    'Talk' : lTalk,
                                                    'ObjectLink' : lObjectLink,
                                                    'Offset' : 'contests',
                                                    'form' : form,
                                                    })       
    
    
@login_required_pro_user
def single_contest_event_draw(request, pContestSlug, pDraw):
    """
    Show all contest results for the specified contest that had the specified draw
    """
    try:
        lContest = Contest.objects.filter(slug=pContestSlug).select_related('contest_type_link')[0]
    except IndexError:
        raise Http404
    
    lResults = ContestResult.objects.filter(contest_event__contest=lContest).filter(Q(draw=pDraw)|Q(draw_second_part=pDraw)).select_related('contest_event', 'band','person_conducting','band__region')
    
    lShowDrawOne = True
    lShowDrawTwo = False
    for result in lResults:
        if result.draw_second_part and int(result.draw_second_part) == int(pDraw):
            lShowDrawTwo = True
            
    return render_auth(request, 'contests/contest_draw.html',  {
                                                              'Contest' : lContest,
                                                              'Results' : lResults,
                                                              'DrawNumber' : pDraw,
                                                              'ShowDrawOne' : lShowDrawOne,
                                                              'ShowDrawTwo' : lShowDrawTwo, 
                                                              })
    
@login_required_pro_user
def single_contest_event_position(request, pContestSlug, pPosition):
    """
    Show all contest results for the specified contest that had the specified position
    """
    try:
        lContest = Contest.objects.filter(slug=pContestSlug).select_related('contest_type_link')[0]
    except IndexError:
        raise Http404
    
    try:
        lPosition = int(pPosition)
        if lPosition == 0:
            lPosition = 9999
    except:
        if pPosition == 'W':
            lPosition = 10001
        elif pPosition == 'D':
            lPosition = 10000
        else:
            lPosition = 9999 
    
    
    lResults = ContestResult.objects.filter(contest_event__contest=lContest).filter(results_position=lPosition).select_related('contest_event', 'band','person_conducting','band__region')
    
    return render_auth(request, 'contests/contest_position.html',  {
                                                              'Contest' : lContest,
                                                              'Results' : lResults,
                                                              'Position' : pPosition,
                                                              })    
    
    
def single_contest_edit_extra_pieces(request, pContestSlug, pContestDate):
    """
    Allow addition of extra pieces stored against each result
    """    
    try:
        lContestEvent = ContestEvent.objects.filter(contest__slug=pContestSlug, date_of_event=pContestDate).select_related('contest')[0]
    except IndexError:
        raise Http404
    
    lResultId = None
    lPieceName = None
    lSuffix = None
    if request.POST:
        for i in request.POST:
            if i.startswith('piece-'):
                lResultId = i[len('piece-'):]
            
        if lResultId:
            lResult = ContestResult.objects.filter(id=lResultId)[0]
            lSuffix = request.POST['suffix-%d' % lResult.id]
            lOrdering = request.POST['ordering-%d' % lResult.id]
            lPieceName = request.POST['piece-%d' % lResult.id]
            try:
                lComposer =  request.POST['composer-%d' % lResult.id]
                lArranger =  request.POST['arranger-%d' % lResult.id]
                lYear =  request.POST['year-%d' % lResult.id]
                lType =  request.POST['type-%d' % lResult.id]
            except KeyError:
                lComposer = None
                lArranger = None
                lYear = None
                lType = None
            try:
                lPiece = TestPiece.objects.filter(name=lPieceName)[0]
                lPieceFound = True
            except IndexError:
                try:
                    lPieceAlias = TestPieceAlias.objects.filter(name=lPieceName)[0]
                    lPiece = lPieceAlias.piece
                    lPieceFound = True
                except IndexError:
                    if lComposer == None:
                        # need to prompt for more details
                        lPieceFound = False 
                    else:
                        # we have more details - create the piece
                        try:
                            lMatchingComposer = Person.objects.filter(combined_name=lComposer)[0]
                        except IndexError:
                            # create composer
                            lMatchingComposer = Person()
                            lMatchingComposer.lastChangedBy = request.user
                            lMatchingComposer.owner = request.user
                            lMatchingComposer.name = lComposer
                            lMatchingComposer.slug = slugify(lComposer)
                            lMatchingComposer.save()
                        lMatchingArranger = None
                        if lArranger:
                            try:
                                lMatchingArranger = Person.objects.filter(combined_name=lArranger)[0]
                            except IndexError:
                                lMatchingArranger = Person()
                                lMatchingArranger.lastChangedBy = request.user
                                lMatchingArranger.owner = request.user
                                lMatchingArranger.name = lArranger
                                lMatchingArranger.slug = slugify(lArranger)
                                lMatchingArranger.save()
                        lPiece = TestPiece()
                        lPiece.lastChangedBy = request.user
                        lPiece.owner = request.user
                        lPiece.name = lPieceName
                        lPiece.slug = slugify(lPieceName)
                        lPiece.year = lYear
                        lPiece.composer = lMatchingComposer
                        lPiece.arranger = lMatchingArranger
                        lPiece.save()
                        lPieceFound = True
        
            if lPieceFound:
                lNewResultPiecePerformance = ResultPiecePerformance()
                lNewResultPiecePerformance.lastChangedBy = request.user
                lNewResultPiecePerformance.owner = request.user
                lNewResultPiecePerformance.result = lResult
                lNewResultPiecePerformance.piece = lPiece
                lNewResultPiecePerformance.suffix = lSuffix
                lNewResultPiecePerformance.ordering = lOrdering
                lNewResultPiecePerformance.save()
    
        if lPieceFound:
            return HttpResponseRedirect('/contests/%s/%s/entertainments/' % (lContestEvent.contest.slug, lContestEvent.date_of_event))
    
    lResults = ContestResult.objects.filter(contest_event=lContestEvent).select_related('band')
    for result in lResults:
        result.extra_pieces = result.resultpieceperformance_set.all().select_related('piece').order_by('ordering')
        result.max_order = 0
        result.show_new_piece_form = False 
        if str(result.id) == lResultId:
            result.show_new_piece_form = True
            result.Suffix = lSuffix
            result.PieceName = lPieceName
        for piece in result.extra_pieces:
            if piece.ordering > result.max_order:
                result.max_order = piece.ordering
        result.next_order = result.max_order + 1
            
    lPieces = TestPiece.objects.all()
    lPieceAliases = TestPieceAlias.objects.all().select_related('piece')
    lPeople = Person.objects.all()
    lPeopleAliases = PersonAlias.objects.all()
    
    return render_auth(request, 'contests/extra_pieces.html', {
                                                               'ContestEvent': lContestEvent,
                                                               'Results' : lResults,
                                                               'Pieces' : lPieces,
                                                               'PieceAliases' : lPieceAliases,
                                                               'People' : lPeople,
                                                               'PeopleAliases' : lPeopleAliases,
                                                               })
    
def single_contest_delete_extra_piece(request, pContestSlug, pContestDate, pExtraPieceId):
    """
    Delete an extra piece
    """    
    try:
        lContestEvent = ContestEvent.objects.filter(contest__slug=pContestSlug, date_of_event=pContestDate).select_related('contest')[0]
        lExtraPiece = ResultPiecePerformance.objects.filter(id=pExtraPieceId)[0]
        lExtraPiece.delete()
    except IndexError:
        raise Http404
    
    return HttpResponseRedirect('/contests/%s/%s/entertainments/' % (lContestEvent.contest.slug, lContestEvent.date_of_event))
    
    
    
