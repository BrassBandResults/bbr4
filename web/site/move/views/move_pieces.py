# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved



from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from bbr.siteutils import browser_details
from bbr.render import render_auth
from contests.models import ContestEvent, ContestResult, ContestTestPiece
from move.models import PieceMergeRequest
from move.tasks import notification
from pieces.models import TestPiece, TestPieceAlias


@login_required
def merge_request(request, pSourcePieceSlug):
    """
    Request move of all results from one piece to another
    """
    try:
        lSourcePiece = TestPiece.objects.filter(slug=pSourcePieceSlug)[0]
        lDestinationPiece = TestPiece.objects.filter(id=request.POST['moveToPiece'])[0]
        
        lPieceMergeRequest = PieceMergeRequest()
        lPieceMergeRequest.source_piece = lSourcePiece
        lPieceMergeRequest.destination_piece = lDestinationPiece
        lPieceMergeRequest.lastChangedBy = request.user
        lPieceMergeRequest.owner = request.user
        lPieceMergeRequest.save()
        
        notification(None, lPieceMergeRequest, 'piece_merge', 'request', request.user, browser_details(request))
    except IndexError:
        # someone already merged one or either side
        pass
        
    return render_auth(request, 'move/merge_request_received.html')
    
    
@login_required
def list_merge_requests(request):
    """
    List all requests for piece merges
    """
    if request.user.profile.superuser == False:
        raise Http404
    
    lMergeRequests = PieceMergeRequest.objects.filter()
    
    return render_auth(request, 'move/list_piece_merge_requests.html', {'MergeRequests' : lMergeRequests})
    
    
@login_required
@csrf_exempt
def reject_merge(request, pMergePieceRequestSerial):
    """
    Reject a piece merge
    """
    if request.user.profile.superuser == False:
        raise Http404
    
    try:
        lPieceMergeRequest = PieceMergeRequest.objects.filter(id=pMergePieceRequestSerial)[0]
    except IndexError:
        raise Http404
    
    # send email back to original submitter
    lReason = request.POST['reason']
    
    if lReason:
        lSubmitterUser = lPieceMergeRequest.owner
        lDestination = lSubmitterUser.email
    else:
        lDestination = 'tsawyer@brassbandresults.co.uk'
    
    lContext = {'Reason' : lReason, }
    notification(None, lPieceMergeRequest, 'piece', 'reject', request.user, browser_details(request), pDestination=lDestination, pAdditionalContext=lContext)
        
    # delete merge request
    lPieceMergeRequest.delete()
    
    return render_auth(request, 'blank.htm')


@login_required
def merge_action(request, pMergePieceRequestSerial):
    """
    Perform a merge of pieces
    """  
    if request.user.profile.superuser == False:
        raise Http404
    
    try:
        lMergeRequest = PieceMergeRequest.objects.filter(id=pMergePieceRequestSerial)[0]
    except IndexError:
        raise Http404
    
    lFromPiece = lMergeRequest.source_piece
    lToPiece = lMergeRequest.destination_piece
    
    # move contest set tests
    lEventsToMove = ContestEvent.objects.filter(test_piece=lFromPiece)
    for event in lEventsToMove:
        event.test_piece = lToPiece
        event.lastChangedBy = request.user
        event.save()
        
    # move own choice results
    lResultsToMove = ContestResult.objects.filter(test_piece=lFromPiece)
    for result in lResultsToMove:
        result.test_piece = lToPiece
        result.lastChangedBy = request.user
        result.save()

    # create piece alias if names different
    if lToPiece.name != lFromPiece.name:
        lNewPieceAlias = TestPieceAlias()
        lNewPieceAlias.piece = lToPiece
        lNewPieceAlias.name = lFromPiece.name
        lNewPieceAlias.owner = request.user
        lNewPieceAlias.lastChangedBy = request.user
        lNewPieceAlias.save()
        
    # move old piece aliases
    for alias in TestPieceAlias.objects.filter(piece=lFromPiece):
        alias.piece = lToPiece
        alias.lastChangedBy = request.user
        alias.save()
        
    # move additional contest test pieces
    for testPiece in ContestTestPiece.objects.filter(test_piece=lFromPiece):
        testPiece.piece = lToPiece
        testPiece.lastChangedBy = request.user
        testPiece.save()
    
        
    notification(None, lMergeRequest, 'piece_merge', 'done', request.user, browser_details(request))
    lSubmitterUser = lMergeRequest.owner
    notification(None, lMergeRequest, 'piece', 'merge', request.user, browser_details(request), pDestination=lSubmitterUser.email)
    
    lFromPiece.delete()
    lMergeRequest.delete()
        
    return HttpResponseRedirect('/move/pieces/')