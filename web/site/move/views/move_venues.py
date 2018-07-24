# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from bbr3.siteutils import browser_details
from bbr3.render import render_auth
from contests.models import Venue, ContestEvent
from contests.models import VenueAlias
from move.models import VenueMergeRequest
from move.tasks import notification


@login_required
def merge_request(request, pSourceVenueSlug):
    """
    Request move of all results from one venue to another
    """
    try:
        lSourceVenue = Venue.objects.filter(slug=pSourceVenueSlug)[0]
        lDestinationVenue = Venue.objects.filter(id=request.POST['moveToVenue'])[0]
        
        lVenueMergeRequest = VenueMergeRequest()
        lVenueMergeRequest.source_venue = lSourceVenue
        lVenueMergeRequest.destination_venue = lDestinationVenue
        lVenueMergeRequest.lastChangedBy = request.user
        lVenueMergeRequest.owner = request.user
        lVenueMergeRequest.save()
        
        notification.delay(None, lVenueMergeRequest, 'venue_merge', 'request', request.user, browser_details(request))
    except IndexError:
        # someone already merged one or either side
        pass        
    
    return render_auth(request, 'move/merge_request_received.html')
    
    
@login_required
def list_merge_requests(request):
    """
    List all requests for venue merges
    """
    if request.user.profile.superuser == False:
        raise Http404
    
    lMergeRequests = VenueMergeRequest.objects.filter()
    
    return render_auth(request, 'move/list_venue_merge_requests.html', {'MergeRequests' : lMergeRequests})
    
    
@login_required
@csrf_exempt
def reject_merge(request, pMergeVenueRequestSerial):
    """
    Reject a venue merge
    """
    if request.user.profile.superuser == False:
        raise Http404
    
    try:
        lVenueMergeRequest = VenueMergeRequest.objects.filter(id=pMergeVenueRequestSerial)[0]
    except IndexError:
        raise Http404
    
    # send email back to original submitter
    lReason = request.POST['reason']
    
    if lReason:
        lSubmitterUser = lVenueMergeRequest.owner
        lDestination = lSubmitterUser.email
    else:
        lDestination = 'tsawyer@brassbandresults.co.uk'
    
    lContext = {'Reason' : lReason, }
    notification.delay(None, lVenueMergeRequest, 'venue', 'reject', request.user, browser_details(request), pDestination=lDestination, pAdditionalContext=lContext)
        
    # delete merge request
    lVenueMergeRequest.delete()
    
    return render_auth(request, 'blank.htm')


@login_required
def merge_action(request, pMergeVenueRequestSerial):
    """
    Perform a merge of venues
    """  
    if request.user.profile.superuser == False:
        raise Http404
    
    try:
        lMergeRequest = VenueMergeRequest.objects.filter(id=pMergeVenueRequestSerial)[0]
    except IndexError:
        raise Http404
    
    lFromVenue = lMergeRequest.source_venue
    lToVenue = lMergeRequest.destination_venue
    
    if not lToVenue.country_id and lFromVenue.country_id: lToVenue.country = lFromVenue.country
    if not lToVenue.latitude and lFromVenue.latitude: lToVenue.latitude = lFromVenue.latitude
    if not lToVenue.longitude and lFromVenue.longitude: lToVenue.longitude = lFromVenue.longitude
    if not lToVenue.postcode and lFromVenue.postcode: lToVenue.postcode = lFromVenue.postcode
    
    lToVenue.save()
    
    lEventsToMove = ContestEvent.objects.filter(venue_link=lFromVenue)
    for event in lEventsToMove:
        event.venue_link = lToVenue
        event.lastChangedBy = request.user
        event.save()
        
    lNewVenueAlias = VenueAlias()
    lNewVenueAlias.venue = lToVenue
    lNewVenueAlias.name = lFromVenue.name
    lNewVenueAlias.owner = request.user
    lNewVenueAlias.lastChangedBy = request.user
    lNewVenueAlias.save()
        
    notification.delay(None, lMergeRequest, 'venue_merge', 'done', request.user, browser_details(request))
    lSubmitterUser = lMergeRequest.owner
    notification.delay(None, lMergeRequest, 'venue', 'merge', request.user, browser_details(request), pDestination=lSubmitterUser.email)
    
    lFromVenue.delete()
    lMergeRequest.delete()
        
    return HttpResponseRedirect('/move/venues/')