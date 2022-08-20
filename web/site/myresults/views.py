# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved



from django.contrib.auth.models import User
from django.http import Http404

from bands.models import Band
from bbr.render import render_auth
from contests.models import Contest, ContestGroup
from people.models import Person
from users.models import PersonalContestHistory


def _show_contest_history_list(request, pUsername, pQuery, pFilter=None, pFilteredTo=None):
    """
    Show contest history if public, based on passed in query of results
    """
    try:
        lUser = User.objects.filter(username=pUsername)[0]
    except IndexError:
        raise Http404
    lProfile = lUser.profile
    if lProfile.contest_history_visibility == 'public':
        lContestHistory = pQuery.filter(user=lUser).exclude(status='pending').select_related()
    else:
        raise Http404

    lResultsWithPositionCount = 0
    lWinsCount = 0
    lTopSixNotWinCount = 0
    lUnplacedCount = 0
    lHistoryBands = {}
    lHistoryConductors = {}
    lTotalPositions = 0.0
    for history in lContestHistory:
        lResultsPosition = history.result.results_position
        lHistoryBands[history.result.band_id] = history.result.band
        if history.result.person_conducting.slug != 'unknown':
            lHistoryConductors[history.result.person_conducting_id] = history.result.person_conducting 
        if lResultsPosition > 0 and lResultsPosition < 9000:
            lTotalPositions += lResultsPosition
            lResultsWithPositionCount += 1
            if lResultsPosition == 1:
                lWinsCount += 1
            elif lResultsPosition <= 6:
                lTopSixNotWinCount += 1
            else:
                lUnplacedCount += 1
        else:
            lUnplacedCount += 1 
            
    lAveragePosition = 0
    if lResultsWithPositionCount > 0:
        lAveragePosition = lTotalPositions / lResultsWithPositionCount
            
    lCurrentUserIsPro = request.user.is_anonymous == False and request.user.profile.pro_member
    lProfileIsForProUser = lProfile.pro_member
    
    lProMember = False
    if lCurrentUserIsPro or lProfileIsForProUser:
        lProMember = True

    return render_auth(request, 'myresults/list.html', {"User" : lUser,
                                                       "UserProfile" : lProfile,
                                                       "ContestHistory" : lContestHistory,
                                                       "ContestResults" : lContestHistory.reverse(),
                                                       "ResultsWithPosition": lResultsWithPositionCount,
                                                        "Wins": lWinsCount,
                                                        "TopSixNotWin":lTopSixNotWinCount,
                                                        "Unplaced": lUnplacedCount,
                                                        "HistoryContestCount" : lContestHistory.count(),
                                                        "BandCount" : len(lHistoryBands),
                                                        "ConductorCount": len(lHistoryConductors),
                                                        "HistoryBands" : lHistoryBands.values(),
                                                        "HistoryConductors" : lHistoryConductors.values(),
                                                        "Filter": pFilter,
                                                        "FilteredTo" : pFilteredTo,
                                                        "ProMember" : lProMember,
                                                        "AveragePosition": lAveragePosition,
                                                       })

def list(request, pUsername):
    """
    Show user's contest history if public
    """
    lQuery = PersonalContestHistory.objects.all()
    return _show_contest_history_list(request, pUsername, lQuery)
    
    
def list_filter_conductor(request, pUsername, pConductorSlug):
    """
    Show contest history filtered to a particular conductor
    """
    lQuery = PersonalContestHistory.objects.filter(result__person_conducting__slug=pConductorSlug)
    try:
        lConductor = Person.objects.filter(slug=pConductorSlug)[0]
    except IndexError:
        raise Http404
    return _show_contest_history_list(request, pUsername, lQuery, "conductor", lConductor)


def list_filter_band(request, pUsername, pBandSlug):
    """
    Show contest history filtered to a particular band
    """
    lQuery = PersonalContestHistory.objects.filter(result__band__slug=pBandSlug)
    try:
        lBand = Band.objects.filter(slug=pBandSlug)[0]
    except IndexError:
        raise Http404
    return _show_contest_history_list(request, pUsername, lQuery, "band", lBand)


def list_filter_contest(request, pUsername, pContestSlug):
    """
    Show contest history filtered to a particular contest
    """
    lQuery = PersonalContestHistory.objects.filter(result__contest_event__contest__slug=pContestSlug)
    try:
        lContest = Contest.objects.filter(slug=pContestSlug)[0]
    except IndexError:
        raise Http404
    return _show_contest_history_list(request, pUsername, lQuery, "contest", lContest)
    
    
def list_filter_group(request, pUsername, pGroupSlug):
    """
    Show contest history filtered to a particular contest group
    """
    lQuery = PersonalContestHistory.objects.filter(result__contest_event__contest__group__slug=pGroupSlug)
    try:
        lContestGroup = ContestGroup.objects.filter(slug=pGroupSlug)[0]
    except IndexError:
        raise Http404
    return _show_contest_history_list(request, pUsername, lQuery, "group", lContestGroup)   
    
    
    
def user_chart_json(request, pUsername):
    """
    Get the json to show the chart for a user's contest history - NOT USED??
    """
    try:
        lUser = User.objects.filter(username=pUsername)[0]
    except IndexError:
        raise Http404()
    
    lProfile = lUser.profile
    if lProfile.contest_history_visibility != 'public':
        raise Http404()
    
    lContestHistory = PersonalContestHistory.objects.filter(user=lUser, status='accepted').select_related()
    
    return render_auth(request, 'myresults/resultschart.json', {"Results" : lContestHistory.reverse(),
                                                                "ShowBand" : True,
                                                                "ShowConductor" : False})        
    
        
    
    
