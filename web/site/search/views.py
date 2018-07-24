# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from django.contrib.contenttypes.models import ContentType
from django.core import urlresolvers
from django.core.urlresolvers import NoReverseMatch
from django.db import connection
from django.http import Http404
from django.utils.datastructures import MultiValueDictKeyError

from bands.models import Band, PreviousBandName
from bbr3.render import render_auth
from contests.models import Contest, Venue, ContestGroup, ContestGroupAlias, ContestAlias
from contests.models import VenueAlias
from people.models import Person, PersonAlias
from pieces.models import TestPiece, TestPieceAlias
from tags.models import ContestTag


class ResultWrapper(object):
    """
    Wrapper class for presenting results to template
    """
    def __init__(self, pObjectToWrapper, pObjectType, pTypeDisplayText=None, pUpperSlug=False, pName=None, pSuffix=None, pOffset=None):
        self.htmlclass = pObjectType
        if pOffset:
            self.url = pOffset
        else:
            self.url = "%ss" % pObjectType
        self.suffix = ""
        if pSuffix:
            self.suffix = pSuffix
        self.slug = pObjectToWrapper.slug
        if pUpperSlug:
            self.slug = self.slug.upper()
        if pName:
            self.name = pName
        else:
            self.name = pObjectToWrapper.name
        if pTypeDisplayText:
            self.type = pTypeDisplayText
        else:
            self.type = pObjectType.title()
        self.title = pObjectToWrapper.name
        try:
            lContentType = ContentType.objects.get_for_model(pObjectToWrapper.__class__)
            self.admin_offset = urlresolvers.reverse("admin:%s_%s_change" % (lContentType.app_label, lContentType.model), args=(pObjectToWrapper.id,))
        except NoReverseMatch:
            self.admin_offset = None
        
class PreviousBandWrapper(object):
    """
    Wrapper class for previous band names
    """
    def __init__(self, pPreviousBandNameObject):
        self.htmlclass = 'band'
        self.url = "bands"
        self.slug = pPreviousBandNameObject.band.slug
        self.name = pPreviousBandNameObject.old_name
        self.type = "Alternative name for %s" % pPreviousBandNameObject.band.name
        self.title = pPreviousBandNameObject.band.name
        
        
class PersonAliasWrapper(object):
    """
    Wrapper class for person aliases
    """
    def __init__(self, pPersonAliasObject):
        self.htmlclass = 'person'
        self.url = "people"
        self.slug = pPersonAliasObject.person.slug
        self.name = pPersonAliasObject.name
        self.type = "Alternative name for %s" % pPersonAliasObject.person.name 
        self.title = pPersonAliasObject.person.name
        

def search(request):
    """
    Show search results
    """
    if not request.GET:
        raise Http404()
    
    try:
        lSearchCriteria = request.GET['q']
    except MultiValueDictKeyError:
        raise Http404()
    if len(lSearchCriteria.strip()) == 0:
        return render_auth(request, 'search/results_blank_search.html', {"SearchCriteria" : lSearchCriteria})
    lResults = []
    lSearchCriteria = lSearchCriteria.strip()
    
    lBands = Band.objects.filter(name__icontains=lSearchCriteria)
    for band in lBands:
        lType = 'Band'
        if band.status != None:
            lType += ' (%s)' % band.get_status_display()
        lResults.append(ResultWrapper(band,'band', pTypeDisplayText=lType, pName=band.name, pSuffix=band.date_range_display))
         
    lContestGroups = ContestGroup.objects.filter(name__icontains=lSearchCriteria)
    for contestGroup in lContestGroups:
        lResults.append(ResultWrapper(contestGroup,'contest', pTypeDisplayText="Contest Group", pUpperSlug=True))
        
    lContestGroupAliases = ContestGroupAlias.objects.filter(name__icontains=lSearchCriteria)
    for groupAlias in lContestGroupAliases:
        lResults.append(ResultWrapper(groupAlias, 'contest', pTypeDisplayText="Contest Group Alias for %s" % groupAlias.group.name, pUpperSlug=True))
        
    lContests = Contest.objects.filter(name__icontains=lSearchCriteria)
    for contest in lContests:
        lResults.append(ResultWrapper(contest,'contest'))
        
    lContestAliases = ContestAlias.objects.filter(name__icontains=lSearchCriteria)
    for contestAlias in lContestAliases:
        lResults.append(ResultWrapper(contestAlias, 'contest', pTypeDisplayText="Contest Alias for %s" % contestAlias.contest.name))
        
    lTestPieces = TestPiece.objects.filter(name__icontains=lSearchCriteria)
    for piece in lTestPieces:
        lResults.append(ResultWrapper(piece,'piece'))
        
    lTestPieceAliases = TestPieceAlias.objects.filter(name__icontains=lSearchCriteria)
    for pieceAlias in lTestPieceAliases:
        lResults.append(ResultWrapper(pieceAlias, 'piece', pTypeDisplayText="Test Piece Alias for %s" % pieceAlias.piece.name))
        
    lPeople = Person.objects.filter(combined_name__icontains=lSearchCriteria)
    for person in lPeople:
        lResults.append(ResultWrapper(person,'person', pOffset='people', pSuffix=person.bandname))
        
    lPeopleAliases = PersonAlias.objects.filter(name__icontains=lSearchCriteria)
    for person_alias in lPeopleAliases:
        lResults.append(PersonAliasWrapper(person_alias))

    lPreviousBandNames = PreviousBandName.objects.filter(old_name__icontains=lSearchCriteria).select_related()
    for previous_name in lPreviousBandNames:
        lResults.append(PreviousBandWrapper(previous_name))
        
    lVenues = Venue.objects.filter(name__icontains=lSearchCriteria)
    for venue in lVenues:
        lResults.append(ResultWrapper(venue, 'venue'))
        
    lVenueAliases = VenueAlias.objects.filter(name__icontains=lSearchCriteria)
    for venue_alias in lVenueAliases:
        lResults.append(ResultWrapper(venue_alias.venue, 'venue', pTypeDisplayText='Other venue name', pName=venue_alias.name))
        
    lContestTags = ContestTag.objects.filter(name__icontains=lSearchCriteria)
    for tag in lContestTags:
        lResults.append(ResultWrapper(tag, 'tag'))
    
    return render_auth(request, 'search/results.html', {"SearchCriteria" : lSearchCriteria,
                                                        "SearchResults" : lResults,
                                                        })