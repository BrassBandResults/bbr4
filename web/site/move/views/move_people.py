# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved



import re

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt

from adjudicators.models import ContestAdjudicator
from bbr.siteutils import browser_details
from bbr.render import render_auth
from contests.models import ContestResult
from move.models import PersonMergeRequest
from bbr.notification import notification
from people.models import Person, PersonAlias, PersonRelation
from people.views import _fetch_adjudication_details
from pieces.models import TestPiece
from web.site.contests.models import CurrentChampion


@login_required
def merge_request(request, pSourcePersonSlug):
    """
    Request move of all results from one person to another
    """
    try:
        lSourcePerson = Person.objects.filter(slug=pSourcePersonSlug)[0]
        lDestinationPerson = Person.objects.filter(id=request.POST['moveToPerson'])[0]
        
        lPersonMergeRequest = PersonMergeRequest()
        lPersonMergeRequest.source_person = lSourcePerson
        lPersonMergeRequest.destination_person = lDestinationPerson
        lPersonMergeRequest.lastChangedBy = request.user
        lPersonMergeRequest.owner = request.user
        lPersonMergeRequest.save()
        
        notification(None, lPersonMergeRequest, 'move', 'person_merge', 'request', request.user, browser_details(request))
    except IndexError:
        # someone already merged one or either side
        pass
    
    return render_auth(request, 'move/merge_request_received.html')
    
    
@login_required
def list_merge_requests(request):
    """
    List all requests for Person merges
    """
    if request.user.profile.superuser == False:
        raise Http404
    
    lMergeRequests = PersonMergeRequest.objects.filter()
    for mergeRequest in lMergeRequests:
        mergeRequest.from_adjuducations_count = ContestAdjudicator.objects.filter(person=mergeRequest.source_person).count()
        mergeRequest.to_adjuducations_count = ContestAdjudicator.objects.filter(person=mergeRequest.destination_person).count()
        
        mergeRequest.from_compositions_count = TestPiece.objects.filter(composer=mergeRequest.source_person).count()
        mergeRequest.to_compositions_count = TestPiece.objects.filter(composer=mergeRequest.destination_person).count()
        
        mergeRequest.from_arranger_count = TestPiece.objects.filter(arranger=mergeRequest.source_person).count()
        mergeRequest.to_arranger_count = TestPiece.objects.filter(arranger=mergeRequest.destination_person).count()
        
    return render_auth(request, 'move/list_person_merge_requests.html', {'MergeRequests' : lMergeRequests})
    
    
@login_required
@csrf_exempt
def reject_merge(request, pMergePersonRequestSerial):
    """
    Reject a Person merge
    """
    if request.user.profile.superuser == False:
        raise Http404
    
    try:
        lPersonMergeRequest = PersonMergeRequest.objects.filter(id=pMergePersonRequestSerial)[0]
    except IndexError:
        raise Http404
    
    # send email back to original submitter
    lReason = request.POST['reason']
    
    if lReason:
        lSubmitterUser = lPersonMergeRequest.owner
        lDestination = lSubmitterUser.email
    else:
        lDestination = 'tsawyer@brassbandresults.co.uk'
    
    lContext = {'Reason' : lReason, }
    notification(None, lPersonMergeRequest, 'move', 'person', 'reject', request.user, browser_details(request), pDestination=lDestination, pAdditionalContext=lContext)
        
    # delete merge request
    lPersonMergeRequest.delete()
    
    return render_auth(request, 'blank.htm')


@login_required
def merge_action(request, pMergePersonRequestSerial):
    """
    Perform a merge of Persons
    """    
    if request.user.profile.superuser == False:
        raise Http404
    
    try:
        lMergeRequest = PersonMergeRequest.objects.filter(id=pMergePersonRequestSerial)[0]
    except IndexError:
        raise Http404
    
    lFromPerson = lMergeRequest.source_person
    lToPerson = lMergeRequest.destination_person
    
    # move results
    lResultsToMove = ContestResult.objects.filter(person_conducting=lFromPerson)
    for result in lResultsToMove:
        result.person_conducting = lToPerson
        if not result.conductor_name:
            result.conductor_name = lFromPerson.name
        result.lastChangedBy = request.user
        result.save()
        
    # move compositions/arrangements
    lCompositionsToMove = TestPiece.objects.filter(composer=lFromPerson)
    for piece in lCompositionsToMove:
        piece.composer = lToPerson
        piece.lastChangedBy = request.user
        piece.save()
    
    lArrangementsToMove = TestPiece.objects.filter(arranger=lFromPerson)
    for piece in lArrangementsToMove:
        piece.arranger = lToPerson
        piece.lastChangedBy = request.user
        piece.save()
    
    # move adjudications
    lContestsToMove = ContestAdjudicator.objects.filter(person=lFromPerson)
    for result in lContestsToMove:
        if not result.adjudicator_name:
            result.adjudicator_name = result.person.name
        result.person = lToPerson
        result.lastChangedBy = request.user
        result.save()
        
    lSourceRelationshipsToMove = PersonRelation.objects.filter(source_person=lFromPerson)
    for relationship in lSourceRelationshipsToMove:
        relationship.source_person = lToPerson
        relationship.lastChangedBy = request.user
        relationship.save()
        
    lDestinationRelationshipsToMove = PersonRelation.objects.filter(relation_person=lFromPerson)
    for relationship in lDestinationRelationshipsToMove:
        relationship.relation_person = lToPerson
        relationship.lastChangedBy = request.user
        relationship.save()

    lChampionsToMove = CurrentChampion.objects.filter(conductor=lFromPerson)
    for champ in lChampionsToMove:
        champ.conductor = lToPerson
        champ.lastChangedBy = request.user
        champ.save()
                
    # Process aliases    
    lInitialRegex = "^\w\.\s\w+$"
    if lFromPerson.name.strip() != lToPerson.name.strip():
        # if it's just initial surname, don't move
        
        lMatches = re.match(lInitialRegex, lFromPerson.name)
        if lMatches == None:
            # does it exist already on destination Person?
            try:
                lExistingAlias = PersonAlias.objects.filter(person=lToPerson, name=lFromPerson.name)[0]
            except IndexError:
                lNewPreviousName = PersonAlias()
                lNewPreviousName.person = lToPerson
                lNewPreviousName.name = lFromPerson.name
                lNewPreviousName.lastChangedBy = request.user
                lNewPreviousName.owner = request.user
                lNewPreviousName.save()
    
    for previous_name in PersonAlias.objects.filter(person=lFromPerson):
        # if it's just initial surname, don't move
        lMatches = re.match(lInitialRegex, previous_name.name)
        if lMatches == None:
            # does it exist already on destination Person?
            try:
                lExistingAlias = PersonAlias.objects.filter(person=lToPerson, name=previous_name.name)[0]
            except IndexError:
                lNewPreviousName = PersonAlias()
                lNewPreviousName.person = lToPerson
                lNewPreviousName.name = previous_name.name
                lNewPreviousName.lastChangedBy = request.user
                lNewPreviousName.owner = request.user
                lNewPreviousName.save()    
                
    notification(None, lMergeRequest, 'move', 'person_merge', 'done', request.user, browser_details(request))
    lSubmitterUser = lMergeRequest.owner
    notification(None, lMergeRequest, 'move', 'person', 'merge', request.user, browser_details(request), pDestination=lSubmitterUser.email)
    
    lFromPerson.delete()
    lMergeRequest.delete()
        
    return HttpResponseRedirect('/move/people/')