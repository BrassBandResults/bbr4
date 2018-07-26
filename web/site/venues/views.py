# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved

from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import Http404, HttpResponseRedirect

from bands.models import Band
from bbr.siteutils import slugify, browser_details
from bbr.render import render_auth
from contests.models import Venue, Contest, ContestEvent
from contests.models import VenueAlias
from regions.models import Region
from .forms import EditVenueForm
from .tasks import notification


def venue_list(request):
    """
    Show a list of a venues
    """
    lVenues = Venue.objects.all()
    lRegions = Region.objects.all()
    lRegionList = {}
    for region in lRegions:
        lRegionList[region.id] = region
    
    # work out events on site for each venue
    cursor = connection.cursor()
    lResults = {}
    cursor.execute("select venue_link_id, count(*) from contests_contestevent group by venue_link_id")
    rows = cursor.fetchall()
    for row in rows:
        lResults[row[0]] = row[1]
    cursor.close()
    
    for venue in lVenues:
        try:
            venue.eventcount = lResults[venue.id]
        except KeyError:
            venue.eventcount = 0
        try:
            venue.country = lRegionList[venue.country_id]
        except KeyError:
            venue.country = None
            
    return render_auth(request, 'venues/venue_list.html', {"Venues" : lVenues})

class ResultObject(object):
    pass

def single_venue(request, pVenueSlug):
    """
    Show details of a single venue
    """
    try:
        lVenue = Venue.objects.filter(slug=pVenueSlug).select_related()[0]
    except IndexError:
        raise Http404()
    
    lContainsVenues = Venue.objects.filter(parent=lVenue)
    
    # select all contest_events for this venue
    cursor = connection.cursor()
    lContestResults = {}
    cursor.execute("SELECT event.id, event.contest_id, contest.name, contest.slug, contest.section_id from contests_contestevent event, contests_contest contest WHERE contest.id = event.contest_id AND event.venue_link_id = %d ORDER BY contest.section_id" % lVenue.id)
    rows = cursor.fetchall()
    for row in rows:
        lContestName = row[2]
        lContestSlug = row[3]
        lPosition = row[4]
        try:
            lCountAlready = lContestResults[lContestSlug].count
            lCountAlready += 1
        except KeyError:
            lCountAlready = 1
            
        lResultsObject = ResultObject()
        lResultsObject.name = lContestName
        lResultsObject.slug = lContestSlug
        lResultsObject.count = lCountAlready
        if lPosition == None:
            lPosition = 99
        lResultsObject.position = lPosition
        
        lContestResults[lContestSlug] = lResultsObject
        
    cursor.close()
    
    lResultsToSort = []
    for lSlug, lResultObject in lContestResults.items():
        lResultsToSort.append((lResultObject.position, lSlug, lResultObject))
        
    lResultsToSort.sort()
    
    lSortedResults = []
    for result in lResultsToSort:
        lSortedResults.append(result[2])
        
    lVenue.contests = lSortedResults
    
    lShowEdit = False
    if request.user.is_anonymous() == False:
        lSuperuser = request.user.profile.superuser or request.user.profile.regional_superuser
        lOwner = request.user.profile.enhanced_functionality and request.user == lVenue.owner
        lShowEdit = lSuperuser or lOwner
        
    lVenueAliases = VenueAlias.objects.filter(venue=lVenue)
    
    return render_auth(request, 'venues/venue.html', {"Venue" : lVenue,
                                                      "Contests" : lSortedResults,
                                                      "ShowEdit" : lShowEdit,
                                                      "Aliases" : lVenueAliases,
                                                      "ContainsVenues" : lContainsVenues,
                                                      })


def single_venue_event(request, pVenueSlug, pContestSlug):
    """
    Show details of which of a particular event have been run at a particular venue
    """
    try:
        lVenue = Venue.objects.filter(slug=pVenueSlug).select_related()[0]
        lContest = Contest.objects.filter(slug=pContestSlug)[0]
    except IndexError:
        raise Http404()
    
    # get events
    cursor = connection.cursor()
    lEvents = []
    lEventIds = ""
    cursor.execute("select event.date_of_event, event.name, contest.slug, contest.name, event.id, contest.id, event.date_resolution from contests_contest contest, contests_contestevent event where contest.slug = '%s' and event.contest_id = contest.id and event.venue_link_id = %d order by event.date_of_event desc" % (pContestSlug, lVenue.id))
    rows = cursor.fetchall()
    if len(rows) == 0:
        raise Http404()
    for row in rows:
        lEvent = ContestEvent()
        lEvent.date_of_event = row[0]
        lEvent.name = row[1]
        lContestSlug = row[2]
        lContestName = row[3]
        lEvent.id = row[4]
        lContestId = row[5]
        lEvent.date_resolution = row[6]
        if len(lEventIds) > 0:
            lEventIds += ','
        lEventIds += str(lEvent.id)
        lEvents.append(lEvent)
    cursor.close()
    
    # get winners
    cursor = connection.cursor()
    lWinners = {}
    cursor.execute("select result.contest_event_id, result.band_name, result.band_id, band.slug, band.name from contests_contestresult result, bands_band band where result.band_id = band.id and result.results_position = 1 and result.contest_event_id in (%s)" % lEventIds)
    rows = cursor.fetchall()
    for row in rows:
        lWinners[row[0]] = (row[1], row[2], row[3], row[4])
    cursor.close()
    
    for lEvent in lEvents:
        if lEvent.id in lWinners.keys():
            lEvent.band_name = lWinners[lEvent.id][0]
            lBand = Band()
            lBand.id = lWinners[lEvent.id][1]
            lBand.slug = lWinners[lEvent.id][2]
            lBand.name = lWinners[lEvent.id][3]
            lEvent.winners = lBand
    
    return render_auth(request, 'venues/event.html', {"Venue" : lVenue,
                                                      "Contest" : lContest,
                                                      "Events" : lEvents,
                                                      })
    
@login_required
def add_venue(request):
    """
    Add a new venue
    """
    lFormType = EditVenueForm
    if request.user.profile.superuser == False:
        if request.user.profile.enhanced_functionality == False:
            raise Http404()
    if request.method == 'POST':
        form = lFormType(request.POST)
        if form.is_valid():
            lNewVenue = form.save(commit=False)
            lNewVenue.slug = slugify(lNewVenue.name, instance=lNewVenue)
            lNewVenue.lastChangedBy = request.user
            lNewVenue.owner = request.user
            lNewVenue.save()
            notification(None, lNewVenue, 'venue', 'new', request.user, browser_details(request))
            return HttpResponseRedirect('/venues/')
    else:
        form = lFormType()

    return render_auth(request, 'venues/new_venue.html', {'form': form})
    
    
@login_required  
def edit_venue(request, pVenueSlug):
    """
    Edit a venue
    """
    try:
        lVenue = Venue.objects.filter(slug=pVenueSlug)[0]
    except IndexError:
        raise Http404()
    
    lSuperuser = request.user.profile.superuser or request.user.profile.regional_superuser
    lOwner = request.user.profile.enhanced_functionality and request.user == lVenue.owner
    lEditAllowed = lSuperuser or lOwner
    if not lEditAllowed:
        raise Http404
        
    lFormClass = EditVenueForm
    if request.method == 'POST':
        form = lFormClass(request.POST, instance=lVenue)
        if form.is_valid():
            lOldVenue = Venue.objects.filter(id=lVenue.id)[0]
            lNewVenue = form.save(commit=False)
            lNewVenue.lastChangedBy = request.user
            lNewVenue.save()
            notification(lOldVenue, lNewVenue, 'venue', 'edit', request.user, browser_details(request))
            return HttpResponseRedirect('/venues/%s/' % lVenue.slug)
    else:
        form = lFormClass(instance=lVenue)

    return render_auth(request, 'venues/edit_venue.html', {'form': form, "Venue" : lVenue}) 


@login_required
def venue_options(request):
    """
    Return <option> tags for droplist of venues
    """
    try:
        lExclude = request.GET['exclude']
        lVenues = Venue.objects.exclude(id=lExclude)
    except KeyError:
        lVenues = Venue.objects.all()
    
    return render_auth(request, 'venues/option_list.htm', {"Venues" : lVenues})   


@login_required
def single_venue_aliases(request, pVenueSlug):
    """
    Show and edit aliases for a given venue
    """
    try:
        lVenue = Venue.objects.filter(slug=pVenueSlug)[0]
    except IndexError:
        raise Http404()
    
    lSuperuser = request.user.profile.superuser
    
    if not (lSuperuser):
        raise Http404()  
    
    if request.POST:
        lNewAlias = request.POST['new_alias_name']
        lVenueAlias = VenueAlias()
        lVenueAlias.venue = lVenue
        lVenueAlias.name = lNewAlias
        lVenueAlias.owner = request.user
        lVenueAlias.lastChangedBy = request.user
        lVenueAlias.save()
        notification(None, lVenueAlias, 'venue_alias', 'new', request.user, browser_details(request))
        return HttpResponseRedirect('/venues/%s/aliases/' % lVenue.slug)
    
    lVenueAliases = VenueAlias.objects.filter(venue=lVenue)
    
    return render_auth(request, "venues/venue_aliases.html", {'Venue' : lVenue,
                                                              'Aliases' : lVenueAliases,
                                                              })


@login_required
def single_venue_alias_delete(request, pVenueSlug, pAliasSerial):
    """
    Delete a band alias
    """
    if request.user.profile.superuser == False:
        raise Http404()
    
    try:
        lVenueAlias = VenueAlias.objects.filter(venue__slug=pVenueSlug, id=pAliasSerial)[0]
    except IndexError:
        raise Http404
    
    notification(None, lVenueAlias, 'venue_alias', 'delete', request.user, browser_details(request))
    lVenueAlias.delete()
    return HttpResponseRedirect('/venues/%s/aliases/' % pVenueSlug)
