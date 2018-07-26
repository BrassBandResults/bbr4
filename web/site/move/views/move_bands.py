# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved


from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from bands.models import Band, PreviousBandName
from bbr.siteutils import browser_details
from bbr.render import render_auth
from contests.models import ContestResult
from move.models import BandMergeRequest
from move.tasks import notification
from users.models import PersonalContestHistoryDateRange


@login_required
def merge_request(request, pSourceBandSlug):
    """
    Request move of all results from one band to another
    """
    try:
        lSourceBand = Band.objects.filter(slug=pSourceBandSlug)[0]
        lDestinationBand = Band.objects.filter(id=request.POST['moveToBand'])[0]
        
        lBandMergeRequest = BandMergeRequest()
        lBandMergeRequest.source_band = lSourceBand
        lBandMergeRequest.destination_band = lDestinationBand
        lBandMergeRequest.lastChangedBy = request.user
        lBandMergeRequest.owner = request.user
        lBandMergeRequest.save()
        
        notification(None, lBandMergeRequest, 'band_merge', 'request', request.user, browser_details(request))
    except IndexError:
        # someone already merged one or either side
        pass        
    return render_auth(request, 'move/merge_request_received.html')
    
    
@login_required
def list_merge_requests(request):
    """
    List all requests for band merges
    """
    if request.user.profile.superuser == False:
        raise Http404
    
    lMergeRequests = BandMergeRequest.objects.filter()
    
    return render_auth(request, 'move/list_band_merge_requests.html', {'MergeRequests' : lMergeRequests})
    
    
@login_required
@csrf_exempt
def reject_merge(request, pMergeBandRequestSerial):
    """
    Reject a band merge
    """
    if request.user.profile.superuser == False:
        raise Http404
    
    try:
        lBandMergeRequest = BandMergeRequest.objects.filter(id=pMergeBandRequestSerial)[0]
    except IndexError:
        raise Http404
    
    # send email back to original submitter
    lReason = request.POST['reason']
    
    if lReason:
        lSubmitterUser = lBandMergeRequest.owner
        lDestination = lSubmitterUser.email
    else:
        lDestination = 'tsawyer@brassbandresults.co.uk'
    
    lContext = {'Reason' : lReason, }
    notification(None, lBandMergeRequest, 'band', 'reject', request.user, browser_details(request), pDestination=lDestination, pAdditionalContext=lContext)
        
    # delete merge request
    lBandMergeRequest.delete()
    
    return render_auth(request, 'blank.htm')


@login_required
def merge_action(request, pMergeBandRequestSerial):
    """
    Perform a merge of bands
    """    
    if request.user.profile.superuser == False:
        raise Http404
    
    try:
        lMergeRequest = BandMergeRequest.objects.filter(id=pMergeBandRequestSerial)[0]
    except IndexError:
        raise Http404
    
    lFromBand = lMergeRequest.source_band
    lToBand = lMergeRequest.destination_band
    
    lContestHistoryDateRangesToMove = PersonalContestHistoryDateRange.objects.filter(band=lFromBand)
    for lDateRange in lContestHistoryDateRangesToMove:
        lDateRange.band = lToBand
        lDateRange.lastChangedBy = request.user
        lDateRange.save()
    
    lResultsToMove = ContestResult.objects.filter(band=lFromBand)
    for result in lResultsToMove:
        result.band = lToBand
        result.lastChangedBy = request.user
        result.save()
        
    lNewPreviousBandName = PreviousBandName()
    lNewPreviousBandName.band = lToBand
    lNewPreviousBandName.old_name = lFromBand.name
    lNewPreviousBandName.hidden = False
    lNewPreviousBandName.owner = request.user
    lNewPreviousBandName.lastChangedBy = request.user
    lNewPreviousBandName.save()
    
    for previous_name in PreviousBandName.objects.filter(band=lFromBand):
        lNewPreviousBandName = PreviousBandName()
        lNewPreviousBandName.band = lToBand
        lNewPreviousBandName.old_name = previous_name.old_name
        lNewPreviousBandName.hidden = previous_name.hidden
        lNewPreviousBandName.owner = previous_name.owner
        lNewPreviousBandName.lastChangedBy = request.user
        lNewPreviousBandName.save()    
        
    notification(None, lMergeRequest, 'band_merge', 'done', request.user, browser_details(request))
    lSubmitterUser = lMergeRequest.owner
    notification(None, lMergeRequest, 'band', 'merge', request.user, browser_details(request), pDestination=lSubmitterUser.email)
    
    lFromBand.delete()
    lMergeRequest.delete()
        
    return HttpResponseRedirect('/move/bands/')


