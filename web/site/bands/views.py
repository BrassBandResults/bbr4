# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.db import connection
from django.db.models.query_utils import Q
from django.template.loader import render_to_string

from bbr.render import render_auth
from bbr.decorators import login_required_pro_user

from bands.models import Band
from bands.forms import EditBandForm, EditBandSuperuserForm, BandTalkEditForm
from contests.models import Contest, ContestGroup, ContestAchievementAward, CurrentChampion, ContestTag

from bbr.siteutils import slugify, browser_details


def check_results_complete(pResults, pContestGroups, pCurrentUser):
    """
    Mark up result position with a tooltip.  Return whether current user is owner of any results and list of conductors involved
    """
    lOwner = False
    lConductors = {}
    if pResults == None:
        return lOwner, lConductors 
    for result in pResults:
        if result.owner == pCurrentUser:
            lOwner = True
        if result.person_conducting:
            lConductors[result.person_conducting.slug] = result.person_conducting
        result.result_tooltip = "%d bands competed at this contest" % result.event_result_count
        result.complete = True
        if not result.marked_complete:
            for group in pContestGroups:
                if group.id == result.contest_event.contest.group_id:
                    result.contest_event.contest.group = group
            
            #if result.event_max_result > result.event_result_count:
            #    result.complete = False
            #if result.event_max_draw > result.event_result_count:
            #    result.complete = False
            if result.event_result_count <= 4:
                result.complete = False
                
            if result.complete == False:
                if result.event_result_count == 1:
                    result.result_tooltip = "We only have 1 record for this contest and so aren't sure how many bands competed.  Please add more results if you know them."
                else:
                    result.result_tooltip = "We only have %d records for this contest and so aren't sure how many bands competed.  Please add more results if you know them." % result.event_result_count
            elif result.event_result_count < 10:
                result.result_tooltip = "About %d bands competed at this contest" % result.event_result_count
    return lOwner, lConductors 


def bands_list(request, pLetter='A'):
    """
    Show a list of all bands beginning with the specified letter
    """
    cursor = connection.cursor()
    lResults = {}
    cursor.execute("select band_id, count(*) from contests_contestresult group by band_id")
    rows = cursor.fetchall()
    for row in rows:
        lResults[row[0]] = row[1]
    cursor.close()
    
    lBandsQuery = Band.objects.all().select_related()
    if pLetter == 'ALL':
        lBands = lBandsQuery
    elif pLetter == '0':
        lBands = lBandsQuery.extra(where=["substr(bands_band.name, 1, 1) in ('0','1','2','3','4','5','6','7','8','9')"])
        pLetter = "0-9"
    else:
        lBands = lBandsQuery.filter(name__istartswith=pLetter)
    for band in lBands:
        try:
            band.resultcount = lResults[band.id]
        except KeyError:
            band.resultcount = 0
    lBandCount = Band.objects.all().count()
    return render_auth(request, 'bands/bands.html', {"Bands" : lBands,
                                                     "ResultCount" : len(lBands),
                                                     "BandCount" : lBandCount,
                                                     "StartsWith" : pLetter})

@login_required  
def add_band(request):
    """
    Add a new band
    """
    if request.user.profile.superuser == False:
        if request.user.profile.enhanced_functionality == False:
            raise Http404()
    if request.method == 'POST':
        form = EditBandForm(request.POST)
        if form.is_valid():
            lNewBand = form.save(commit=False)
            lNewBand.slug = slugify(lNewBand.name, instance=lNewBand)
            lNewBand.lastChangedBy = request.user
            lNewBand.owner = request.user
            lNewBand.save()
            notification(None, lNewBand, 'band', 'new', request.user, browser_details(request))
            return HttpResponseRedirect('/bands/')
    else:
        form = EditBandForm()

    return render_auth(request, 'bands/new_band.html', {'form': form})
    
    
@login_required  
def edit_band(request, pBandSlug):
    """
    Edit a band
    """
    try:
        lBand = Band.objects.filter(slug=pBandSlug)[0]
    except IndexError:
        raise Http404()
    
    lSuperuser = request.user.profile.superuser
    lEnhancedUserAndOwner = request.user.profile.enhanced_functionality and lBand.owner == request.user
    lRegionalSuperuserAndBandInRightRegion = request.user.profile.is_regional_superuser_region(lBand.region)   
    lRegionalSuperuser = request.user.profile.regional_superuser
    
    if not (lSuperuser or lEnhancedUserAndOwner or lRegionalSuperuserAndBandInRightRegion or lRegionalSuperuser):
        raise Http404
        
    if lSuperuser or lRegionalSuperuserAndBandInRightRegion:
        lFormClass = EditBandSuperuserForm
    else:
        lFormClass = EditBandForm
    if request.method == 'POST':
        form = lFormClass(request.POST, instance=lBand)
        if form.is_valid():
            lOldBand = Band.objects.filter(id=lBand.id)[0]
            lNewBand = form.save(commit=False)
            
            if lNewBand.name.lower() != lOldBand.name.lower():
                try:
                    lOldBandMatchingAlias = PreviousBandName.objects.filter(band=lNewBand, old_name__iexact=lOldBand.name)[0]
                except IndexError:
                    # old name doesn't exist as alias
                    lPreviousBandName = PreviousBandName()
                    lPreviousBandName.owner = request.user
                    lPreviousBandName.lastChangedBy = request.user
                    lPreviousBandName.original_owner = request.user
                    lPreviousBandName.old_name = lOldBand.name
                    lPreviousBandName.visible = True
                    lPreviousBandName.band = lNewBand
                    lPreviousBandName.save()
                
            lNewBand.lastChangedBy = request.user
            lNewBand.save()
            
            notification(lOldBand, lNewBand, 'band', 'edit', request.user, browser_details(request))

            return HttpResponseRedirect('/bands/%s/' % lBand.slug)
    else:
        form = lFormClass(instance=lBand)

    return render_auth(request, 'bands/edit_band.html', {'form': form, "Band" : lBand})    

   
class TwitterReturn(object):
    pass   
   
def single_band(request, pBandSlug, pFilterContestGroupSlug=None, pFilterContestSlug=None, pFilterTagSlug=None):
    """
    Show details of a single band.  
    
    If pContestGroupSlug is populated, show results filtered to that group.
    If pContestSlug is populated, show results filtered to that contest
    If pFilterTagSlug is populated, show results filtered to contests tagged with that tag
    """
    
    try:
        lBand = Band.objects.filter(slug=pBandSlug)[0]
    except IndexError:
        raise Http404()
        
    lTemplate = 'bands/band.html'
    
    lContestGroups = ContestGroup.objects.all()
    
    lResults = lBand.contestresult_set.extra(select={
                                 'event_result_count' : "SELECT count(*) FROM contests_contestresult cr WHERE cr.contest_event_id=contests_contestresult.contest_event_id",
                                 'event_max_result' : "SELECT max(results_position) FROM contests_contestresult cr WHERE cr.contest_event_id=contests_contestresult.contest_event_id",
                                 'event_max_draw' : "SELECT max(draw) FROM contests_contestresult cr WHERE cr.contest_event_id=contests_contestresult.contest_event_id",
                                 'marked_complete' : "SELECT complete FROM contests_contestevent ce WHERE ce.id=contests_contestresult.contest_event_id",
                                 },).select_related('contest_event', 'contest_event__contest','contest_event__contest__group', 'person_conducting', 'owner')
    
    lRunsBase = ContestAchievementAward.objects.filter(band=lBand).filter(award="run")
    
    lFilterSlug = None
    lFilteredTo = None
    if pFilterContestSlug:
        # Contest Filter
        lFilterSlug = pFilterContestSlug
        lContestFilterSlug = pFilterContestSlug
        try:
            lFilterContest = Contest.objects.filter(slug=lContestFilterSlug)[0]
            lFilteredTo = lFilterContest
        except IndexError:
            raise Http404
        if lResults.count() == 0:
            raise Http404()
        lContestResults = lResults.exclude(contest_event__contest__group__group_type='W').filter(band=lBand, contest_event__contest__slug=lContestFilterSlug).select_related()
        lWhitFridayResults = None # don't show whit friday results if filtering
        lWins = lBand.wins.filter(contest_event__contest__slug=lContestFilterSlug).count()
        lSeconds = lBand.seconds.filter(contest_event__contest__slug=lContestFilterSlug).count()
        lThirds = lBand.thirds.filter(contest_event__contest__slug=lContestFilterSlug).count()
        lTopSixNotWin = lBand.top_six_not_win.filter(contest_event__contest__slug=lContestFilterSlug).count()
        lUnplaced = lBand.unplaced.filter(contest_event__contest__slug=lContestFilterSlug).count()
        lResultsWithPosition = lBand.results_with_placings.filter(contest_event__contest__slug=lContestFilterSlug).count()
        lRuns = lRunsBase.filter(contest=lFilterContest)
        
    
    elif pFilterContestGroupSlug:
        # Group Filter
        lFilterSlug = pFilterContestGroupSlug
        lGroupFilterSlug = pFilterContestGroupSlug.lower()
        try:
            lFilterGroup = ContestGroup.objects.filter(slug=lGroupFilterSlug)[0]
            lFilteredTo = lFilterGroup
        except IndexError:
            raise Http404
        lContestResults = lResults.exclude(contest_event__contest__group__group_type='W').filter(band=lBand, contest_event__contest__group__slug=lGroupFilterSlug).select_related()
        lWhitFridayResults = None # don't show whit friday results if filtering
        lWins = lBand.wins.filter(contest_event__contest__group__slug=lGroupFilterSlug).count()
        lSeconds = lBand.seconds.filter(contest_event__contest__group__slug=lGroupFilterSlug).count()
        lThirds = lBand.thirds.filter(contest_event__contest__group__slug=lGroupFilterSlug).count()
        lTopSixNotWin = lBand.top_six_not_win.filter(contest_event__contest__group__slug=lGroupFilterSlug).count()
        lUnplaced = lBand.unplaced.filter(contest_event__contest__group__slug=lGroupFilterSlug).count()
        lResultsWithPosition = lBand.results_with_placings.filter(contest_event__contest__group__slug=lGroupFilterSlug).count()
        lRuns = lRunsBase.filter(contest__group=lFilterGroup)
       
    else:
        # No Filter
        lContestResults = lResults.exclude(contest_event__contest__group__group_type='W')
        lWhitFridayResults = lResults.filter(contest_event__contest__group__group_type='W')
        lWins = len(lBand.wins)
        lSeconds = len(lBand.seconds)
        lThirds = len(lBand.thirds)
        lTopSixNotWin = len(lBand.top_six_not_win)
        lUnplaced = len(lBand.unplaced)
        lResultsWithPosition = len(lBand.results_with_placings)
        lRuns = lRunsBase.filter(band=lBand)
        
    lResultOwner, lContestConductors = check_results_complete(lContestResults, lContestGroups, request.user)
    lWhitFridayOwner, lWhitFridayConductors = check_results_complete(lWhitFridayResults, lContestGroups, request.user)
    if len(lRuns) == 0:
        lRuns = None     
        
    lShowTabs = False
    if lWhitFridayResults and lWhitFridayResults.count() > 0 and lContestResults.count() > 0:
        lShowTabs = True
    elif lRuns and len(lRuns) > 0:
        lShowTabs = True
        
    lConductors = {}
    lConductors.update(lWhitFridayConductors)
    
    lWhitFridayMarches = {}
    if lWhitFridayResults:
        lWhitFridayMarches['unknown'] = None
        for result in lWhitFridayResults:
            if result.test_piece:
                lWhitFridayMarches[result.test_piece.slug] = result.test_piece

    lStartDate = lBand.start_date or (lBand.first_parent and lBand.first_parent.end_date) or (lBand.second_parent and lBand.second_parent.end_date)
    lEndDate = lBand.end_date
    
    lShowOnMap = False
    if lBand.longitude and lBand.latitude and len(lBand.longitude) > 0 and len(lBand.latitude) > 0:
        lShowOnMap = True
    lShowEdit = False
    if request.user.is_anonymous() == False:
        lSuperuser = request.user.profile.superuser
        lEnhancedFunctionalityAndOwner = request.user.profile.enhanced_functionality and request.user == lBand.owner
        lRegionalSuperuserAndBandInRightRegion = request.user.profile.is_regional_superuser_region(lBand.region) 
        lRegionalSuperuser = request.user.profile.regional_superuser
        lShowEdit = lSuperuser or lEnhancedFunctionalityAndOwner or lRegionalSuperuserAndBandInRightRegion or lRegionalSuperuser
        lWhitFridayOwner = lWhitFridayOwner or request.user.profile.superuser
        
    lFirstResultYear = None
    if lBand.earliest_result():
        lFirstResultYear = lBand.earliest_result().contest_event.date_of_event.year
    lLastResultYear = None
    if lBand.latest_result():
        lLastResultYear = lBand.latest_result().contest_event.date_of_event.year
    
    # twitter
    try:
        lAuth = tweepy.OAuthHandler(settings.TWEEPY_CONSUMER_TOKEN, settings.TWEEPY_CONSUMER_SECRET)
        lAuth.set_access_token(settings.TWEEPY_ACCESS_TOKEN_KEY, settings.TWEEPY_ACCESS_TOKEN_SECRET)
        lApi = tweepy.API(lAuth)
        lTwitter = TwitterReturn()
        lTwitter.user = lApi.get_user(lBand.twitter_name)
        lTwitter.timeline = lTwitter.user.timeline()
        lTwitter.status = lTwitter.timeline[0]
    except:
        lTwitter = None
        
    lCurrentChampions = CurrentChampion.objects.filter(band=lBand)
    lAwards = ContestAchievementAward.objects.filter(band=lBand).exclude(award='Hat trick')
    
    lDescendants = Band.objects.filter(Q(first_parent=lBand)|Q(second_parent=lBand))
    lAncestors = []
    if lBand.first_parent:
        lAncestors.append(lBand.first_parent)
    if lBand.second_parent:
        lAncestors.append(lBand.second_parent)
        
    if pFilterTagSlug:
        try:
            lContestTag = ContestTag.objects.filter(slug=pFilterTagSlug)[0]
        except IndexError:
            raise Http404
        lFilteredResults = []
        for result in lContestResults:
            for tag in result.contest_event.tag_list():
                if lContestTag.id == tag.id:
                    lFilteredResults.append(result)
                    break
        lContestResults = lFilteredResults
        lFilteredTo = lContestTag

    
    return render_auth(request, lTemplate, {        "Band" : lBand,
                                                    "ContestResults" : lContestResults,
                                                    "WhitFridayResults" : lWhitFridayResults, 
                                                    "Wins": lWins,
                                                    "Seconds": lSeconds,
                                                    "Thirds": lThirds,
                                                    "TopSixNotWin": lTopSixNotWin,
                                                    "Unplaced": lUnplaced,
                                                    "ResultsWithPosition" : lResultsWithPosition,
                                                    "WhitFridayOwner" : lWhitFridayOwner,
                                                    "ResultOwner" : lResultOwner,
                                                    "ShowTabs" : lShowTabs,
                                                    "BandConductors" : lConductors.values(),
                                                    "BandMarches" : lWhitFridayMarches.values(),
                                                    "StartDate" : lStartDate,
                                                    "EndDate" : lEndDate,
                                                    "ShowOnMap" : lShowOnMap,
                                                    "ShowEdit" : lShowEdit,
                                                    "FirstResultYear" : lFirstResultYear,
                                                    "LastResultYear" : lLastResultYear,
                                                    "Twitter" : lTwitter,
                                                    "CurrentChampions" : lCurrentChampions,
                                                    "Awards" : lAwards,
                                                    "BandSection" : lBand.section,
                                                    "Aliases" : lBand.previous_band_names(),
                                                    "Filter" : pFilterContestSlug or pFilterContestGroupSlug or pFilterTagSlug,
                                                    "FilterSlug" : lFilterSlug,
                                                    "FilteredTo" : lFilteredTo,
                                                    "Runs" : lRuns,
                                                    "Descendants" : lDescendants,
                                                    "Ancestors" : lAncestors,
                                                    })


@login_required_pro_user
def single_band_filter(request, pBandSlug, pContestSlug):
    """
    Show details of a single band filtered to a specific contest
    """
    return single_band(request, pBandSlug, pFilterContestSlug=pContestSlug)


@login_required_pro_user
def single_band_filter_group(request, pBandSlug, pContestGroupSlug):
    """
    Show details of a single band filtered to a specific contest group
    """
    return single_band(request, pBandSlug, pFilterContestGroupSlug=pContestGroupSlug)


@login_required_pro_user
def single_band_filter_tag(request, pBandSlug, pTagSlug):
    """
    Show details of a single band filtered to a specific contest tag
    """
    return single_band(request, pBandSlug, pFilterTagSlug=pTagSlug)


@login_required
def single_band_aliases(request, pBandSlug):
    """
    Show and edit aliases for a given band
    """
    try:
        lBand = Band.objects.filter(slug=pBandSlug)[0]
    except IndexError:
        raise Http404()
    
    lSuperuser = request.user.profile.superuser
    lEnhancedUserAndOwner = request.user.profile.enhanced_functionality and lBand.owner == request.user
    
    if not (lSuperuser or lProfileOwner or lEnhancedUserAndOwner):
        raise Http404()  
    
    if request.POST:
        lNewAlias = request.POST['new_alias_name']
        lBandAlias = PreviousBandName()
        lBandAlias.band = lBand
        lBandAlias.old_name = lNewAlias
        lBandAlias.owner = request.user
        lBandAlias.lastChangedBy = request.user
        lBandAlias.save()
        notification(None, lBandAlias, 'band_alias', 'new', request.user, browser_details(request))
        return HttpResponseRedirect('/bands/%s/aliases/' % lBand.slug)
    
    lBandAliases = PreviousBandName.objects.filter(band=lBand)
    
    return render_auth(request, "bands/band_aliases.html", {'Band' : lBand,
                                                            'Aliases' : lBandAliases,
                                                            })
    
    
@login_required
def single_band_alias_show(request, pBandSlug, pAliasSerial):
    """
    Show an alias on the conductor page
    """
    try:
        lBand = Band.objects.filter(slug=pBandSlug)[0]
    except IndexError:
        raise Http404()
    
    lSuperuser = request.user.profile.superuser
    lEnhancedUserAndOwner = request.user.profile.enhanced_functionality and lBand.owner == request.user
    
    if not (lSuperuser or lEnhancedUserAndOwner):
        raise Http404()  
    
    try:
        lBandAlias = PreviousBandName.objects.filter(band__slug=pBandSlug, id=pAliasSerial)[0]
    except IndexError:
        raise Http404
    
    lBandAlias.hidden = False
    lBandAlias.lastChangedBy = request.user
    lBandAlias.save()
    notification(None, lBandAlias, 'band_alias', 'show', request.user, browser_details(request))
    return HttpResponseRedirect('/bands/%s/aliases/' % pBandSlug)


@login_required
def single_band_alias_hide(request, pBandSlug, pAliasSerial):
    """
    Hide an alias on the band page
    """
    try:
        lBand = Band.objects.filter(slug=pBandSlug)[0]
    except IndexError:
        raise Http404()
    
    lSuperuser = request.user.profile.superuser
    lEnhancedUserAndOwner = request.user.profile.enhanced_functionality and lBand.owner == request.user
    
    if not (lSuperuser or lEnhancedUserAndOwner):
        raise Http404()  
    
    try:
        lBandAlias = PreviousBandName.objects.filter(band__slug=pBandSlug, id=pAliasSerial)[0]
    except IndexError:
        raise Http404
    
    lBandAlias.hidden = True
    lBandAlias.lastChangedBy = request.user
    lBandAlias.save()
    notification(None, lBandAlias, 'band_alias', 'hide', request.user, browser_details(request))
    return HttpResponseRedirect('/bands/%s/aliases/' % pBandSlug)


@login_required
def single_band_alias_delete(request, pBandSlug, pAliasSerial):
    """
    Delete a band alias
    """
    if request.user.profile.superuser == False:
        raise Http404()
    
    try:
        lBandAlias = PreviousBandName.objects.filter(band__slug=pBandSlug, id=pAliasSerial)[0]
    except IndexError:
        raise Http404
    
    notification(None, lBandAlias, 'band_alias', 'delete', request.user, browser_details(request))
    lBandAlias.delete()
    return HttpResponseRedirect('/bands/%s/aliases/' % pBandSlug)



def chart_json(request, pBandSlug):
    """
    Return the data for a band chart of results
    """
    try:
        lBand = Band.objects.filter(slug=pBandSlug)[0]
    except IndexError:
        raise Http404()
    return render_auth(request, 'bands/resultschart.json', {"Results" : lBand.reverse_results(),
                                                            "ShowBand" : False,
                                                            "ShowConductor" : True})
    
def chart_json_filter(request, pBandSlug, pContestSlug):
    """
    Return the data for a band chart of results
    """
    try:
        lBand = Band.objects.filter(slug=pBandSlug)[0]
    except IndexError:
        raise Http404()
    return render_auth(request, 'bands/resultschart.json', {"Results" : lBand.reverse_results(pContestSlug),
                                                            "ShowBand" : False,
                                                            "ShowConductor" : True})
    
    
def chart_json_filter_group(request, pBandSlug, pContestGroupSlug):
    """
    Return the data for a band chart of results
    """
    try:
        lBand = Band.objects.filter(slug=pBandSlug)[0]
    except IndexError:
        raise Http404()
    return render_auth(request, 'bands/resultschart.json', {"Results" : lBand.reverse_results(pContestGroupSlug),
                                                            "ShowBand" : False,
                                                            "ShowConductor" : True})
    
def band_results_embed(request, pBandSlug):
    """
    Show instructions on how to embed contest results on other website
    """
    try:
        lBand = Band.objects.filter(slug=pBandSlug)[0]
    except IndexError:
        raise Http404()
    lBandSlugUnderscores = lBand.slug.replace('-','_')
    return render_auth(request, 'bands/embed.html', {"Band" : lBand,
                                                     "BandSlugUnderscores" : lBandSlugUnderscores})
    
@login_required
def update_whit_friday_conductors(request, pBandSlug):
    """
    Submit contains post parameters, with conductor slug to use, and several parameters starting with select-n where n is a contest result serial
    Update the specified results to have the specified conductor
    """
    if request.method == "GET":
        raise Http404
    
    lConductorSlug = request.POST['WhitFridayConductor']
    lMarchSlug = request.POST['WhitFridayMarch']
    
    try:
        lConductor = Person.objects.filter(slug=lConductorSlug)[0]
    except IndexError:
        raise Http404
    
    lMarch = None
    if lMarchSlug != None and len(lMarchSlug) > 0 and lMarchSlug!= 'unknown':
        try:
            lMarch = TestPiece.objects.filter(slug=lMarchSlug)[0]
        except IndexError:
            raise Http404
    
    for key, value in request.POST.items():
        if key.startswith('select-'):
            lResultSerial = key[len('select-'):]
            lResult = ContestResult.objects.filter(id=lResultSerial)[0]
            lResult.person_conducting = lConductor
            lResult.test_piece = lMarch 
            if request.user.profile.superuser:
                lOldResult = ContestResult.objects.filter(id=lResult.id)[0]
                lResult.save()
                contest_notification(lOldResult, lResult, 'contest_result', 'edit', request.user, browser_details(request))
            
    return HttpResponseRedirect('/bands/%s/#whitfriday-tab' % pBandSlug)


@login_required_pro_user
def band_results_csv(request, pBandSlug):
    """
    Return band's results as a CSV file
    """
    try:
        lBand = Band.objects.filter(slug=pBandSlug)[0]
    except IndexError:
        raise Http404()
    lResults = lBand.contestresult_set.extra(select={
                                 'event_result_count' : "SELECT count(*) FROM contests_contestresult cr WHERE cr.contest_event_id=contests_contestresult.contest_event_id",
                                 'event_max_result' : "SELECT max(results_position) FROM contests_contestresult cr WHERE cr.contest_event_id=contests_contestresult.contest_event_id",
                                 'event_max_draw' : "SELECT max(draw) FROM contests_contestresult cr WHERE cr.contest_event_id=contests_contestresult.contest_event_id",
                                 'marked_complete' : "SELECT complete FROM contests_contestevent ce WHERE ce.id=contests_contestresult.contest_event_id",
                                 },).select_related()
    lContestResults = lResults.exclude(contest_event__contest__group__group_type='W')
    lWhitFridayResults = lResults.filter(contest_event__contest__group__group_type='W')
    
    lCsvFile = render_to_string('bands/results.csv', {"Band" : lBand,
                                                      "ContestResults" : lContestResults,
                                                      "WhitFridayResults" : lWhitFridayResults,
                                                      })
    
    lResponse = HttpResponse(content_type="text/csv")
    lResponse['Content-Disposition'] = "attachment; filename=%s.csv" % lBand.slug
    lResponse.write(lCsvFile)
    return lResponse


@login_required
def band_options(request):
    """
    Return <option> tags for droplist of bands
    """
    try:
        lExclude = request.GET['exclude']
        lBands = Band.objects.exclude(id=lExclude)
    except KeyError:
        lBands = Band.objects.all()
    
    return render_auth(request, 'bands/option_list.htm', {"Bands" : lBands})


@login_required
def talk(request, pSlug):
    """
    Show the talk page for a particular band
    """
    if request.user.profile.superuser == False:
        raise Http404
   
    try:
        lObjectLink = Band.objects.filter(slug=pSlug)[0]
    except IndexError:
        raise Http404
    
    try:
        lTalk = BandTalkPage.objects.filter(object_link=lObjectLink)[0]
    except IndexError:
        lTalk = None
        
    lRecentTalkChanges = fetch_recent_talk_changes(request)
        
    return render_auth(request, 'talk/talk.html', {
                                                    'Talk' : lTalk,
                                                    'ObjectLink' : lObjectLink,
                                                    'Offset' : 'bands',
                                                    'RecentTalkChanges' : lRecentTalkChanges,
                                                   })
    
@login_required
def talk_edit(request, pSlug):
    """
    Edit the talk page
    """
    if request.user.profile.superuser == False:
        raise Http404
    
    try:
        lObjectLink = Band.objects.filter(slug=pSlug)[0]
    except IndexError:
        raise Http404
    
    try:
        lTalk = BandTalkPage.objects.filter(object_link=lObjectLink)[0]
    except IndexError:
        lTalk = BandTalkPage()
        lTalk.lastChangedBy = request.user
        lTalk.owner = request.user
        lTalk.object_link = lObjectLink
        lTalk.save()
        
    if request.method == "POST":
        form = BandTalkEditForm(data=request.POST, instance=lTalk)
        if form.is_valid():
            lTalk = form.save(commit=False)
            lTalk.lastChangedBy = request.user
            lTalk.owner = request.user
            lTalk.object_link = lObjectLink
            lTalk.save()
            return HttpResponseRedirect('/bands/%s/talk/' % lObjectLink.slug)
        
    else:
        form = BandTalkEditForm(instance=lTalk)        
        
    return render_auth(request, 'talk/talk_edit.html', {
                                                    'Talk' : lTalk,
                                                    'ObjectLink' : lObjectLink,
                                                    'Offset' : 'bands',
                                                    'form' : form,
                                                    })        
    
@login_required_pro_user
def delete_single_band(request, pSlug):
    """
    Delete a band
    """
    if request.user.profile.superuser == False:
        raise Http404
    
    try:
        lBand = Band.objects.filter(slug=pSlug)[0]
    except IndexError:
        raise Http404
    
    lResultsCount = ContestResult.objects.filter(band_id=lBand.id).count()
    
    if (lResultsCount > 0):
        raise Http404
    
    lBand.delete()
    
    return HttpResponseRedirect('/bands/')


class ResultObject:
    pass  

@login_required_pro_user
def contest_winners(request):
    """
    Show list of which bands have won the most contests, excluding whit friday
    """
    lBands = []
    cursor = connection.cursor()
    
    cursor.execute("""
WITH 
  winners AS
   (SELECT band_id, count(*) as winners
    FROM contests_contestresult r
    INNER JOIN contests_contestevent e ON e.id = r.contest_event_id
    INNER JOIN contests_contest c ON c.id = e.contest_id
    WHERE r.results_position = 1
    AND (c.group_id is null or c.group_id NOT IN (509,76,77)) -- whit friday Rochdale/Tameside/Saddleworth
    GROUP BY band_id),
  total AS
   (SELECT band_id, count(*) as contests
    FROM contests_contestresult r
    INNER JOIN contests_contestevent e ON e.id = r.contest_event_id
    INNER JOIN contests_contest c ON c.id = e.contest_id
    AND (c.group_id is null or c.group_id NOT IN (509,76,77)) -- whit friday Rochdale/Tameside/Saddleworth
    AND r.results_position < 1000
    GROUP BY band_id)
SELECT b.slug, b.name, w.winners, t.contests
FROM bands_band b
INNER JOIN winners w ON b.id = w.band_id
INNER JOIN total t ON b.id = t.band_id
ORDER BY 3 desc""") 
    rows = cursor.fetchall()
    for row in rows:
        lBand = ResultObject()
        lBand.slug = row[0]
        lBand.name = row[1]
        lBand.wins = row[2]
        lBand.contests = row[3]
        lBand.percent_win = (lBand.wins * 100) // lBand.contests
        if lBand.contests >= 10:
            lBands.append(lBand)
    cursor.close()
    return render_auth(request, 'bands/winners.html', {
                                                       'Bands' : lBands,
                                                       })
   
