# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from django.db import connection
from django.http import Http404, HttpResponseRedirect

from bands.models import Band
from bbr3.decorators import login_required_pro_user
from bbr3.render import render_auth
from contests.models import ContestEvent, Contest, LOWEST_SPECIAL_POSITION
from people.models import Person


@login_required_pro_user
def bands_home(request):
    """
    Show option to allow bands to be compared
    """
    if request.POST:
        lBandOneSlug = request.POST['first_band']
        lBandTwoSlug = request.POST['second_band']
        return HttpResponseRedirect('/compare/bands/%s/%s/' % (lBandOneSlug, lBandTwoSlug))
    else:
        lBands = Band.objects.all()
        return render_auth(request, "compare/bands/compare.html", {"Bands": lBands,})
    
class Result(object):
    pass
    
def _compare_band_results(pBandOne, pBandTwo, pContestSlug):
    """
    Build contest comparison list
    """
    lReturn = []
    cursor = connection.cursor()
    lResults = {}
    cursor.execute("""
    SELECT
  band_one_result.results_position, band_two_result.results_position, event.date_of_event, contest.slug, contest.name, event.date_resolution

FROM
  contests_contestresult band_one_result,
  contests_contestresult band_two_result,
  contests_contestevent event,
  contests_contest contest

WHERE band_one_result.band_id = %d
AND band_two_result.band_id = %d
AND band_one_result.contest_event_id = band_two_result.contest_event_id
AND event.id = band_one_result.contest_event_id
AND event.contest_id = contest.id
ORDER BY event.date_of_event desc
    """ % (pBandOne.id, pBandTwo.id))
    rows = cursor.fetchall()
    lContestEvent = ContestEvent()
    lBandOneWins = 0
    lBandTwoWins = 0
    for row in rows:
        lResult = Result()
        lResult.slug = row[3]
        lResult.name = row[4]
        if lResult.name.find('(Whit Friday)') > 0:
            continue
        if pContestSlug and lResult.slug != pContestSlug:
            continue
        lResult.band_one_position = row[0]
        lResult.band_two_position = row[1]
        lResult.band_one = lResult.band_one_position
        lResult.band_two = lResult.band_two_position
        if int(lResult.band_one) > LOWEST_SPECIAL_POSITION or int(lResult.band_two) > LOWEST_SPECIAL_POSITION:
            continue
        elif lResult.band_one == lResult.band_two:
            lResult.band_one = '<span class="BandOneBar">&nbsp;%s&nbsp;</span>' % lResult.band_one
            lResult.band_two = '<span  class="BandTwoBar">&nbsp;%s&nbsp;</span>' % lResult.band_two
        elif lResult.band_one < lResult.band_two:
            lResult.band_one = '<span class="BandOneBar">&nbsp;%s&nbsp;</span>' % lResult.band_one
            lBandOneWins += 1
        else:
            lResult.band_two = '<span  class="BandTwoBar">&nbsp;%s&nbsp;</span>' % lResult.band_two
            lBandTwoWins += 1
        lResult.date = row[2]
        lResult.date_resolution = row[5]
        lContestEvent.date_of_event = lResult.date
        lContestEvent.date_resolution = lResult.date_resolution
        lResult.event_date = lContestEvent.event_date
        lReturn.append(lResult)
    cursor.close()
    return (lReturn, lBandOneWins, lBandTwoWins)
        

@login_required_pro_user
def band_compare(request, pBandOneSlug):
    """
    Compare the specified band to another
    """
    try:
        lBandOne = Band.objects.filter(slug=pBandOneSlug)[0]
    except IndexError:
        raise Http404()
    
    if request.POST:
        lBandOneSlug = request.POST['first_band']
        lBandTwoSlug = request.POST['second_band']
        return HttpResponseRedirect('/compare/bands/%s/%s/' % (lBandOneSlug, lBandTwoSlug))
    else:
        lBands = Band.objects.exclude(slug=lBandOne.slug)
        return render_auth(request, "compare/bands/compare_this_another.html", {"BandOne" : lBandOne,
                                                                                "Bands": lBands,
                                                                               })
        
    
def _did_you_mean_process_band(pResultsArray, pBandOne, pBandTwo):
    """
    Add comparison structure to results array if there are results to show
    """
    lResultsArray = pResultsArray
    if pBandTwo:
        lResults = _compare_band_results(pBandOne, pBandTwo, None)
        if len(lResults[0]) > 0:
            lResultsTuple = (lResults, pBandOne, pBandTwo)
            lResultsArray.append(lResultsTuple)
    return lResultsArray
        
        
def _did_you_mean_bands(pBandOne, pBandTwo):
    """
    Try a match a little looser, based on band parents
    """
    try:
        lBandTwoAsParentOne = Band.objects.filter(first_parent=pBandTwo)[0]
    except IndexError:
        lBandTwoAsParentOne = None
    try:
        lBandTwoAsParentTwo = Band.objects.filter(second_parent=pBandTwo)[0]
    except IndexError:
        lBandTwoAsParentTwo = None
    lBandTwoFirstParent = pBandTwo.first_parent
    lBandTwoSecondParent = pBandTwo.second_parent
    
    lResults = []
    lResults = _did_you_mean_process_band(lResults, pBandOne, lBandTwoAsParentOne)
    lResults = _did_you_mean_process_band(lResults, pBandOne, lBandTwoAsParentTwo)
    lResults = _did_you_mean_process_band(lResults, pBandOne, lBandTwoFirstParent)
    lResults = _did_you_mean_process_band(lResults, pBandOne, lBandTwoSecondParent)
    
    # convert return to sensible structure
    lReturnArray = []
    for result in lResults:
        lDataItem = {}
        lDataItem['bandOne'] = result[1]
        lDataItem['bandTwo'] = result[2]
        lDataItem['winsOne'] = result[0][1]
        lDataItem['winsTwo'] = result[0][2]
        lReturnArray.append(lDataItem)
    return lReturnArray            
    
    

@login_required_pro_user    
def bands_compare(request, pBandOneSlug, pBandTwoSlug):
    """
    Compare two bands
    """
    return bands_compare_contest(request, pBandOneSlug, pBandTwoSlug, None)

    
@login_required_pro_user    
def bands_compare_contest(request, pBandOneSlug, pBandTwoSlug, pContestSlug):
    """
    Compare two bands, optionally limited to specific contest
    """
    if pBandOneSlug == pBandTwoSlug:
        return render_auth(request, "compare/bands/cant_compare_with_self.html")    
    
    try:
        lBandOne = Band.objects.filter(slug=pBandOneSlug)[0]
        lBandTwo = Band.objects.filter(slug=pBandTwoSlug)[0]
    except IndexError:
        raise Http404()
    
    lCompareResults, lBandOneWins, lBandTwoWins = _compare_band_results(lBandOne, lBandTwo, pContestSlug)
    try:
        lBandOnePercent = (lBandOneWins * 100) / (lBandOneWins + lBandTwoWins)
        lBandTwoPercent = (lBandTwoWins * 100) / (lBandOneWins + lBandTwoWins)
    except:
        lBandOnePercent = 0
        lBandTwoPercent = 0
        
        
    lDidYouMean = None
    if len(lCompareResults) == 0:
        lDidYouMean = _did_you_mean_bands(lBandOne, lBandTwo)
    
    lContestName = None
    if pContestSlug:
        try:
            lContest = Contest.objects.filter(slug=pContestSlug)[0]
            lContestName = lContest.name
        except:
            raise Http404
        
    
    return render_auth(request, "compare/bands/compare_result.html", {"BandOne" : lBandOne,
                                                                      "BandTwo" : lBandTwo,
                                                                      "CompareResults" : lCompareResults,
                                                                      "BandOneWins" : lBandOneWins,
                                                                      "BandTwoWins" : lBandTwoWins,
                                                                      "BandOnePercent" : lBandOnePercent,
                                                                      "BandTwoPercent" : lBandTwoPercent,
                                                                      "DidYouMean" : lDidYouMean,
                                                                      "ContestSlug" : pContestSlug,
                                                                      "ContestName" : lContestName,
                                                                      "Filter" : pContestSlug != None
                                                                      })
    
    
@login_required_pro_user
def conductors_home(request):
    """
    Show option to allow bands to be compared
    """
    if request.POST:
        lConductorOneSlug = request.POST['first_conductor']
        lConductorTwoSlug = request.POST['second_conductor']
        return HttpResponseRedirect('/compare/conductors/%s/%s/' % (lConductorOneSlug, lConductorTwoSlug))
    else:
        lConductors = Person.objects.all()
        return render_auth(request, "compare/conductors/compare.html", {"Conductors": lConductors,})
    
   
def _compare_conductor_results(pConductorOne, pConductorTwo, pContestSlug):
    """
    Build contest comparison list
    """
    lReturn = []
    cursor = connection.cursor()
    lResults = {}
    cursor.execute("""
    SELECT
  conductor_one_result.results_position, conductor_two_result.results_position, event.date_of_event, contest.slug, contest.name, event.date_resolution, conductor_one_result.band_name, conductor_two_result.band_name

FROM
  contests_contestresult conductor_one_result,
  contests_contestresult conductor_two_result,
  contests_contestevent event,
  contests_contest contest

WHERE conductor_one_result.person_conducting_id = %d
AND conductor_two_result.person_conducting_id = %d
AND conductor_one_result.contest_event_id = conductor_two_result.contest_event_id
AND event.id = conductor_one_result.contest_event_id
AND event.contest_id = contest.id
ORDER BY event.date_of_event desc
    """ % (pConductorOne.id, pConductorTwo.id))
    rows = cursor.fetchall()
    lContestEvent = ContestEvent()
    lConductorOneWins = 0
    lConductorTwoWins = 0
    for row in rows:
        lResult = Result()
        lResult.slug = row[3]
        lResult.name = row[4]
        if lResult.name.find('(Whit Friday)') > 0:
            continue
        if pContestSlug and lResult.slug != pContestSlug:
            continue        
        lResult.conductor_one_position = row[0]
        lResult.conductor_two_position = row[1]
        lResult.conductor_one = lResult.conductor_one_position
        lResult.conductor_two = lResult.conductor_two_position
        if int(lResult.conductor_one) > LOWEST_SPECIAL_POSITION or int(lResult.conductor_two) > LOWEST_SPECIAL_POSITION:
            continue
        elif lResult.conductor_one == lResult.conductor_two:
            lResult.conductor_one = '<span class="BandOneBar">&nbsp;%s&nbsp;</span>' % lResult.conductor_one
            lResult.conductor_two = '<span  class="BandTwoBar">&nbsp;%s&nbsp;</span>' % lResult.conductor_two
        elif lResult.conductor_one < lResult.conductor_two:
            lResult.conductor_one = '<span class="BandOneBar">&nbsp;%s&nbsp;</span>' % lResult.conductor_one
            lConductorOneWins += 1
        else:
            lResult.conductor_two = '<span  class="BandTwoBar">&nbsp;%s&nbsp;</span>' % lResult.conductor_two
            lConductorTwoWins += 1
        lResult.date = row[2]
        lResult.date_resolution = row[5]
        lResult.conductor_one_band_name = row[6]
        lResult.conductor_two_band_name = row[7]
        lContestEvent.date_of_event = lResult.date
        lContestEvent.date_resolution = lResult.date_resolution
        lResult.event_date = lContestEvent.event_date
        lReturn.append(lResult)
    cursor.close()
    return (lReturn, lConductorOneWins, lConductorTwoWins)
        
    
@login_required_pro_user
def conductor_compare(request, pConductorOneSlug):
    """
    Compare the specified band to another
    """
    try:
        lConductorOne = Person.objects.filter(slug=pConductorOneSlug)[0]
    except IndexError:
        raise Http404()
    
    if request.POST:
        lConductorOneSlug = request.POST['first_conductor']
        lConductorTwoSlug = request.POST['second_conductor']
        return HttpResponseRedirect('/compare/conductors/%s/%s/' % (lConductorOneSlug, lConductorTwoSlug))
    else:
        lConductors = Person.objects.exclude(slug=lConductorOne.slug)
        return render_auth(request, "compare/conductors/compare_this_another.html", {"ConductorOne" : lConductorOne,
                                                                                     "Conductors": lConductors,
                                                                                    })

@login_required_pro_user
def conductors_compare(request, pConductorOneSlug, pConductorTwoSlug):
    """
    Compare two conductors
    """
    return conductors_compare_contest(request, pConductorOneSlug, pConductorTwoSlug, None)


@login_required_pro_user
def conductors_compare_contest(request, pConductorOneSlug, pConductorTwoSlug, pContestSlug):
    """
    Compare two conductors, optionally filtering to a contest
    """
    if pConductorOneSlug == pConductorTwoSlug:
        return render_auth(request, "compare/conductors/cant_compare_with_self.html")    
    
    try:
        lConductorOne = Person.objects.filter(slug=pConductorOneSlug)[0]
        lConductorTwo = Person.objects.filter(slug=pConductorTwoSlug)[0]
    except IndexError:
        raise Http404()
    
    lCompareResults, lConductorOneWins, lConductorTwoWins = _compare_conductor_results(lConductorOne, lConductorTwo, pContestSlug)
    try:
        lConductorOnePercent = (lConductorOneWins * 100) / (lConductorOneWins + lConductorTwoWins)
        lConductorTwoPercent = (lConductorTwoWins * 100) / (lConductorOneWins + lConductorTwoWins)
    except:
        lConductorOnePercent = 0
        lConductorTwoPercent = 0
        
    lContestName = None
    if pContestSlug:
        lContest = Contest.objects.filter(slug=pContestSlug)[0]
        lContestName = lContest.name
        
    return render_auth(request, "compare/conductors/compare_result.html", {"ConductorOne" : lConductorOne,
                                                                           "ConductorTwo" : lConductorTwo,
                                                                           "CompareResults" : lCompareResults,
                                                                           "ConductorOneWins" : lConductorOneWins,
                                                                           "ConductorTwoWins" : lConductorTwoWins,
                                                                           "ConductorOnePercent" : lConductorOnePercent,
                                                                           "ConductorTwoPercent" : lConductorTwoPercent,
                                                                           "ContestSlug" : pContestSlug,
                                                                           "ContestName" : lContestName,
                                                                           "Filter" : pContestSlug != None
                                                                           })
    