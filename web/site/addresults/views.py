# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import Http404, HttpResponseRedirect
from django.utils.datastructures import MultiValueDictKeyError

from addresults.forms import ContestNameForm, ContestDateForm, ResultsForm, NotesForm, ContestTypeForm
from adjudicators.models import ContestAdjudicator
from bands.models import Band, PreviousBandName
from bbr.notification import notification
from bbr.siteutils import add_space_after_dot, add_dot_after_initial, slugify, browser_details
from bbr.render import render_auth    
from contests.models import Contest, ContestEvent, Venue, ContestResult
from contests.models import VenueAlias
from people.models import PersonAlias, Person
from pieces.models import TestPiece, TestPieceAlias
from regions.models import Region


@login_required
def enter_contest_name(request):
    """
    Enter the name of the contest
    """
    lForm = ContestNameForm()
    lContestName = ''
    if request.POST:
        lForm = ContestNameForm(request.POST)
        lContestName = request.POST['contest']
        if lForm.is_valid():
            lContestName = lForm.cleaned_data['contest']
            if lContestName.strip().endswith('.'):
                lContestName = lContestName.strip()[:-1]
            lExistingContest = False
            try:
                lContest = Contest.objects.filter(name__iexact=lContestName)[0]
                lContestGroup = lContest.group
                if lContestGroup and lContestGroup.group_type == 'W':
                    return HttpResponseRedirect("/addresults/whitfriday")
                lExistingContest = True
            except IndexError:
                lContest = Contest()
                lContest.name = lContestName
                lContest.slug = slugify(lContestName, instance=lContest)
                lContest.description = ''
                lContest.lastChangedBy = request.user
                lContest.owner = request.user
                lContest.save() 
                
                notification(None, lContest, 'contests', 'contest', 'new', request.user, browser_details(request))
                
            if lExistingContest:
                return HttpResponseRedirect('/addresults/%s/' % lContest.slug)
            else:
                return HttpResponseRedirect('/addresults/%s/contest-type/' % lContest.slug)
            
    cursor = connection.cursor()
    lContestNamesData = []
    cursor.execute("select name from contests_contest order by name")
    rows = cursor.fetchall() 
    for row in rows:
        lContestNamesData.append(row[0])
    return render_auth(request, 'addresults/contestname.html', {'form' : lForm,
                                                                'value' : lContestName,
                                                                'Data' : lContestNamesData})
    
    
@login_required
def enter_contest_type(request, pContestSlug):
    """
    Enter the type of contest
    """
    try:
        lContest = Contest.objects.filter(slug=pContestSlug)[0]
    except IndexError:
        raise Http404()
    
    if request.POST:
        lForm = ContestTypeForm(request.POST, instance=lContest)
        if lForm.is_valid():
            lContestType = lForm.cleaned_data['contest_type_link']
            lContest.contest_type_link = lContestType
            lContest.save()
            return HttpResponseRedirect('/addresults/%s/' % lContest.slug)
    else:
        lForm = ContestTypeForm(instance=lContest)
    return render_auth(request, 'addresults/contesttype.html', {"Contest" : lContest,
                                                                "form" : lForm})
    

@login_required    
def enter_contest_date(request, pContestSlug):
    """
    Enter date of contest
    """
    lContestDate = ""
    lForm = ContestDateForm()
    try:
        lContest = Contest.objects.filter(slug=pContestSlug)[0]
    except IndexError:
        raise Http404()
    if request.POST:
        lForm = ContestDateForm(request.POST)
        lContestDate = request.POST['ContestDate']
        if lForm.is_valid():
            lContestDate = lForm.cleaned_data['ContestDate'].strip()
            lSlashCount = lContestDate.count('/')
            if lSlashCount == 0:
                lDay, lMonth, lYear = (1,1, lContestDate)
                lDateResolution = 'Y'
            elif lSlashCount == 1:
                lDay = 1
                lMonth, lYear = lContestDate.split('/')
                lDateResolution = 'M'
            elif lSlashCount == 2:
                lDay, lMonth, lYear = lContestDate.split('/')
                lDateResolution = 'D'
            lDate = '%s-%s-%s' % (lYear, lMonth, lDay)
            try:
                lContestEvent = ContestEvent.objects.filter(contest=lContest, date_of_event=lDate)[0]
                lResultCount = ContestResult.objects.filter(contest_event=lContestEvent).count()
                if lResultCount > 0:
                    return HttpResponseRedirect('/addresults/exists/%s/%s/' % (pContestSlug, lDate))
                else:
                    return HttpResponseRedirect('/addresults/%s/%s/5/' % (pContestSlug, lDate))
            except IndexError:
                lContestEvent = ContestEvent()
                lContestEvent.date_of_event = date(int(lYear), int(lMonth), int(lDay))
                lContestEvent.date_resolution = lDateResolution
                lContestEvent.contest = lContest
                lContestEvent.name = lContest.name
                lContestEvent.lastChangedBy = request.user
                lContestEvent.owner = request.user
                lContestEvent.save()
                
                notification(None, lContestEvent, 'contests', 'contestevent', 'new', request.user, browser_details(request))
                
            if lContestEvent.contest_type.test_piece:
                return HttpResponseRedirect('/addresults/%s/%s/' % (pContestSlug, lDate))
            else:
                return HttpResponseRedirect('/addresults/%s/%s/3/' % (pContestSlug, lDate))
    lToday = date.today()
    lYesterday = date.today() - timedelta(days=1)
    return render_auth(request, 'addresults/contestdate.html', {"Contest" : lContest,
                                                                "value" : lContestDate,
                                                                "form" : lForm,
                                                                "Today" : lToday,
                                                                "Yesterday" : lYesterday,
                                                                })
    
@login_required
def enter_test_piece(request, pContestSlug, pDate):
    """
    Enter test piece
    """
    try:
        lContest = Contest.objects.filter(slug=pContestSlug)[0]
        lContestEvent = ContestEvent.objects.filter(contest=lContest, date_of_event=pDate)[0]
    except IndexError:
        raise Http404()
    if request.POST:
        lTestPieceName = request.POST['TestPiece']
        lTestPieceName = lTestPieceName.strip()
        if lTestPieceName.endswith('.'):
            lTestPieceName = lTestPieceName[:-1] 
        if lTestPieceName.lower() == "unknown":
            lTestPieceName = ''
        if lTestPieceName.lower().startswith("own choice"):
            lTestPieceName = ''
        if lTestPieceName.lower() == "own choice test piece":
            lTestPieceName = ''
        if len(lTestPieceName) > 0:
            try:
                lTestPiece = TestPiece.objects.filter(name__iexact=lTestPieceName)[0]
            except IndexError:
                try:
                    lTestPieceAlias = TestPieceAlias.objects.filter(name__iexact=lTestPieceName)[0]
                    lTestPiece = lTestPieceAlias.piece
                except IndexError:
                    lTestPiece = TestPiece()
                    lTestPiece.name = lTestPieceName
                    lTestPiece.slug = slugify(lTestPieceName, instance=lTestPiece)
                    lTestPiece.lastChangedBy = request.user
                    lTestPiece.owner = request.user
                    lTestPiece.save()
                    
                    notification(None, lTestPiece, 'pieces', 'piece', 'new', request.user, browser_details(request))
                    
            lContestEvent.test_piece = lTestPiece
            lContestEvent.save()
            
        return HttpResponseRedirect('/addresults/%s/%s/3/' % (pContestSlug, pDate))
    else:
        cursor = connection.cursor()
        lTestPieceNamesData = []
        cursor.execute("select name from pieces_testpiece order by name")
        rows = cursor.fetchall() 
        for row in rows:
            lTestPieceNamesData.append(row[0])
        cursor.close()
        cursor = connection.cursor()
        cursor.execute("select name from pieces_testpiecealias order by name")
        rows = cursor.fetchall() 
        for row in rows:
            lTestPieceNamesData.append(row[0])
        cursor.close()
        return render_auth(request, 'addresults/testpiece.html', {"Contest" : lContest,
                                                                  "ContestEvent" : lContestEvent,
                                                                  "Data" : lTestPieceNamesData,
                                                                 })
     
@login_required
def enter_composer(request, pContestSlug, pDate):
    """
    Enter composer for test piece, only shown if we don't match an existing piece
    """
    try:
        lContest = Contest.objects.filter(slug=pContestSlug)[0]
        lContestEvent = ContestEvent.objects.filter(contest=lContest, date_of_event=pDate)[0]
    except IndexError:
        raise Http404()
    
    if request.POST:
        lComposerName = add_space_after_dot(request.POST['Composer'])
        lLastSpace = lComposerName.rfind(' ')
        if lLastSpace > 0:
            lComposerFirstNames = lComposerName[:lLastSpace].strip()
            lComposerSurname = lComposerName[lLastSpace:].strip()
        else:
            lComposerSurname = lComposerName 
            lComposerFirstNames = ''
            
        lArrangerName = add_space_after_dot(request.POST['Arranger'])
        lArrangerFirstNames = ''
        lArrangerSurname = ''
        if len(lArrangerName.strip()) > 0:
            lLastSpace = lArrangerName.rfind(' ')
            if lLastSpace > 0:
                lArrangerFirstNames = lArrangerName[:lLastSpace].strip()
                lArrangerSurname = lArrangerName[lLastSpace:].strip()
            else:
                lArrangerSurname = lArrangerName
        
        
        lArrangerPerson = None
        lComposerPerson = None
        
        lTestPiece = lContestEvent.test_piece
        if len(lComposerName.strip()) > 0:
            try:
                lComposerPerson = Person.objects.filter(surname__iexact=lComposerSurname, first_names__iexact=lComposerFirstNames)[0]
            except IndexError:
                try:
                    lPersonAlias = PersonAlias.objects.filter(name__iexact=lComposerName)[0]
                    lArrangerPerson = lPersonAlias.person
                except IndexError:
                    lPerson = Person()
                    lPerson.surname = lComposerSurname
                    lPerson.first_names = lComposerFirstNames
                    lPerson.slug = slugify(lComposerName, instance=lPerson)
                    lPerson.owner = request.user
                    lPerson.lastChangedBy = request.user
                    lPerson.save()
                    lArrangerPerson = lPerson
                    notification(None, lPerson, 'people', 'person', 'new', request.user, browser_details(request)) 
                
        if len(lArrangerName.strip()) > 0:
            try:
                lArrangerPerson = Person.objects.filter(surname__iexact=lArrangerSurname, first_names__iexact=lArrangerFirstNames)[0]
            except IndexError:
                try:
                    lPersonAlias = PersonAlias.objects.filter(name__iexact=lArrangerName)[0]
                    lArrangerPerson = lPersonAlias.person
                except IndexError:
                    lPerson = Person()
                    lPerson.surname = lArrangerSurname
                    lPerson.first_names = lArrangerFirstNames
                    lPerson.slug = slugify(lArrangerName, instance=lPerson)
                    lPerson.owner = request.user
                    lPerson.lastChangedBy = request.user
                    lPerson.save()
                    lArrangerPerson = lPerson
                    notification(None, lPerson, 'people', 'person', 'new', request.user, browser_details(request))                
                
        lTestPiece.arranger = lArrangerPerson
        lTestPiece.composer = lComposerPerson
        lTestPiece.save()
        return HttpResponseRedirect('/addresults/%s/%s/4/' % (pContestSlug, pDate))
    else:
        if lContestEvent.test_piece == None or lContestEvent.test_piece.composer or lContestEvent.test_piece.arranger:
            return HttpResponseRedirect('/addresults/%s/%s/4/' % (pContestSlug, pDate))
        else:
            cursor = connection.cursor()
            lComposerNames = []
            cursor.execute("select first_names || ' ' || surname || ' ' || coalesce (suffix, '') from people_person order by 1")
            rows = cursor.fetchall() 
            for row in rows:
                lComposerNames.append(row[0].strip())
            cursor.close()
            
            return render_auth(request, 'addresults/composer.html', {"Contest" : lContest,
                                                                     "ContestEvent" : lContestEvent,
                                                                     "Data" : lComposerNames,
                                                                    })
            
@login_required
def enter_venue(request, pContestSlug, pDate):
    """
    Enter venue, default to the last place this contest ran at
    """
    try:
        lContest = Contest.objects.filter(slug=pContestSlug)[0]
        lContestEvent = ContestEvent.objects.filter(contest=lContest, date_of_event=pDate)[0]
    except IndexError:
        raise Http404()
    
    if request.POST:
        lVenue = request.POST['Venue'].strip()
        if lVenue.lower() == 'venue, town':
            lVenue = ''
        if len(lVenue) > 0:
            if lVenue.endswith('.'):
                lVenue = lVenue[:-1]
            try:
                lMatchingVenue = Venue.objects.filter(name__iexact=lVenue)[0]
                lContestEvent.venue_link = lMatchingVenue
            except IndexError:
                try:
                    lMatchingVenueAlias = VenueAlias.objects.filter(name__iexact=lVenue)[0]
                    lContestEvent.venue_link = lMatchingVenueAlias.venue    
                except IndexError:
                    lNewVenue = Venue()
                    lNewVenue.name = lVenue
                    lNewVenue.lastChangedBy = request.user
                    lNewVenue.owner = request.user
                    lNewVenue.slug = slugify(lNewVenue.name, instance=lNewVenue)
                    lNewVenue.save()
                    notification(None, lNewVenue, 'venues', 'venue', 'new', request.user, browser_details(request))
                    lContestEvent.venue_link = lNewVenue
        lContestEvent.save()
        
        return HttpResponseRedirect('/addresults/%s/%s/5/' % (pContestSlug, pDate))
    else:
        try:
            lLatestContestEvent = ContestEvent.objects.filter(contest=lContest).order_by('-date_of_event')[1]
            try:
                lPreviousVenue = lLatestContestEvent.venue_link.name
            except AttributeError:
                lPreviousVenue = "Venue, Town"
        except IndexError:
            lPreviousVenue = "Venue, Town"
        
        cursor = connection.cursor()
        lVenueNamesData = []
        cursor.execute("select * from (select name from contests_venue union select name from venues_venuealias) x order by name")
        rows = cursor.fetchall() 
        for row in rows:
            lVenueNamesData.append(row[0])
        return render_auth(request, 'addresults/venue.html', {"Contest" : lContest,
                                                              "ContestEvent" : lContestEvent,
                                                              "PreviousVenue" : lPreviousVenue,
                                                              "Data" : lVenueNamesData,
                                                             })
        
_CONDUCTOR_PREFIX = '<ul class="errorlist"><li>Can&#39;t find conductor &#39;'
_BAND_PREFIX = '<ul class="errorlist"><li>Can&#39;t find band &#39;'
            
@login_required
def enter_results(request, pContestSlug, pDate):
    """
    Enter the actual results of the contest
    """
    lForm = ResultsForm()
    lHowToCorrectErrors = ''
    try:
        lContest = Contest.objects.filter(slug=pContestSlug)[0]
        lContestEvent = ContestEvent.objects.filter(contest=lContest, date_of_event=pDate)[0]
    except IndexError:
        raise Http404()
    
    # if flag is set, forward to adjudicator and don't allow results to be added
    lToday = date.today()
    if lToday < lContestEvent.date_of_event and lContest.prevent_future_bands:
        return HttpResponseRedirect('/addresults/%s/%s/6/' % (pContestSlug, pDate))
        
    if request.POST:
        try:
            lRadioSelection = request.POST['conductor_choice']
            if lRadioSelection == 'newconductor':
                lNewConductorPerson = Person()
                lNewConductorPerson.name = request.POST['conductor']
                lNewConductorPerson.slug = slugify(lNewConductorPerson.name, instance=lNewConductorPerson)
                lNewConductorPerson.lastChangedBy = request.user
                lNewConductorPerson.owner = request.user
                lNewConductorPerson.save()
                notification(None, lNewConductorPerson, 'people', 'person', 'new', request.user, browser_details(request))
                
            elif lRadioSelection == 'alias':
                lPreviousConductorName = request.POST['conductoralias']
                lConductorSerial = request.POST['conductorid']
                
                lConductor = Person.objects.filter(id=int(lConductorSerial))[0]
                lPreviousName = PersonAlias()
                lPreviousName.name = lPreviousConductorName
                lPreviousName.person = lConductor
                lPreviousName.lastChangedBy = request.user
                lPreviousName.owner = request.user
                lPreviousName.save()
                notification(None, lPreviousName, 'people', 'person_alias', 'new', request.user, browser_details(request))
                
                ## TODO create person alias here - we'll need to pass through the person id, not the conductor id
            
        except MultiValueDictKeyError:
            pass
        
        try:
            lRadioSelection = request.POST['band']
            if lRadioSelection == 'newband':
                # create a new band
                lNewBandName = request.POST['newbandname']
                lNewBandRegion = request.POST['newbandregion']
                lNewBand = Band()
                lNewBand.name = lNewBandName
                lNewBand.slug = slugify(lNewBandName, instance=lNewBand)
                lNewBand.region = Region.objects.filter(id=lNewBandRegion)[0]
                lNewBand.owner = request.user
                lNewBand.lastChangedBy = request.user
                lNewBand.save()
                notification(None, lNewBand, 'bands', 'band', 'new', request.user, browser_details(request))
            elif lRadioSelection == 'nameonly':
                lPreviousBandName = request.POST['oldbandname']
                lBandSerial = request.POST['bandid']
                lBand = Band.objects.filter(id=int(lBandSerial))[0]
                lPreviousName = PreviousBandName()
                lPreviousName.old_name = lPreviousBandName
                lPreviousName.band = lBand
                lPreviousName.lastChangedBy = request.user
                lPreviousName.owner = request.user
                lPreviousName.save()
                notification(None, lPreviousName, 'bands', 'band_alias', 'new', request.user, browser_details(request))
        except MultiValueDictKeyError:
            pass
        
        lForm = ResultsForm(request.POST)
        lForm.event = lContestEvent
        if lForm.is_valid():
            lForm.save(request, lContestEvent)
            return HttpResponseRedirect('/addresults/%s/%s/6/' % (pContestSlug, pDate))
        else:
            lFormErrors = str(lForm.errors['results'])
            if lFormErrors.startswith(_CONDUCTOR_PREFIX):
                lConductorName = lFormErrors[len(_CONDUCTOR_PREFIX):-15]
                lConductorDropList = '<select name="conductorid">\n'
                lConductors = Person.objects.all()
                for conductor in lConductors:
                    lAdd = True
                    if conductor.end_date and lContestEvent.date_of_event > conductor.end_date:
                        lAdd = False
                    elif conductor.start_date and lContestEvent.date_of_event < conductor.start_date:
                        lAdd = False
                    if lAdd:
                        lConductorDropList = lConductorDropList + '<option value="%s">%s, %s</option>\n' % (conductor.id, conductor.surname, conductor.first_names)
                lConductorDropList = lConductorDropList + '</select>'

                lHowToCorrectErrors = """<input type="radio" name="conductor_choice" value="newconductor"/>Next submit will create a new conductor called: <input type="text" name="conductor" value="%s"/><br/>
                                         <input type="radio" name="conductor_choice" value="alias"/>Next submit will add a conductor alias of <b>%s</b> to %s<input type="hidden" name="conductoralias" value="%s"/><br/>
                                         <input type="radio" name="conductor_choice" value="nothing" checked="checked"/>Do nothing, correct it in the text box below.""" % (lConductorName, lConductorName, lConductorDropList, lConductorName)
            if lFormErrors.startswith(_BAND_PREFIX):
                lBandName = lFormErrors[len(_BAND_PREFIX):-15]
                #lBandName = lFormErrors[len(_BAND_PREFIX):-15]
                lBandDropList = '<select name="bandid">\n'
                lBands = Band.objects.all()
                for band in lBands:
                    lAdd = True
                    if band.end_date and lContestEvent.date_of_event > band.end_date:
                        lAdd = False
                    elif band.start_date and lContestEvent.date_of_event < band.start_date:
                        lAdd = False
                    if lAdd:
                        lBandDropList = lBandDropList + '<option value="%s">%s</option>\n' % (band.id, band.name)
                lBandDropList = lBandDropList + '</select>'
                lRegionDropList = ""
                lContestRegion = "Unknown"
                if lContest.region:
                    lContestRegion = lContest.region.name
                for region in Region.objects.all():
                    lRegionDropList += "<option value='" + str(region.id) + "'"
                    if region.name == lContestRegion:
                        lRegionDropList += " selected='selected'" 
                    lRegionDropList += ">" + region.name + "</option>\n"
                lHowToCorrectErrors = """You have two choices to fix this problem.  You can either create a new band, or assign this name as an old name of an already existing band.  Use existing bands where possible.<br/>
                                         <input type="radio" name="band" value="newband"/>Next submit will create a new band called: <input type="text" name="newbandname" value="%s"/> in <select name="newbandregion">%s</select> region<br/>
                                         <input type="radio" name="band" value="nameonly"/>Next submit will add a previous band name to %s called <b>%s</b><input type="hidden" name="oldbandname" value="%s"/><br/>
                                         <input type="radio" name="band" value="nothing" checked="checked"/>Do nothing, correct it in the text box below.
                                         """ % (lBandName, lRegionDropList, lBandDropList, lBandName, lBandName)
                                         
    
    return render_auth(request, 'addresults/bands.html', {"Contest" : lContest,
                                                          "ContestEvent" : lContestEvent,
                                                          "form" : lForm,
                                                          "HowToCorrectErrors" : lHowToCorrectErrors,
                                                          })
    
    
@login_required
def amend_results(request, pContestSlug, pDate):
    """
    Update the existing results of the contest
    """
    try:
        lContest = Contest.objects.filter(slug=pContestSlug)[0]
        lContestEvent = ContestEvent.objects.filter(contest=lContest, date_of_event=pDate)[0]
    except IndexError:
        raise Http404()
    lExistingUnplacedResults = ContestResult.objects.filter(contest_event=lContestEvent).order_by('results_position', 'band_name').select_related()
    lEnhancedFunctionality = request.user.profile.enhanced_functionality
    if lEnhancedFunctionality == False:
        lExistingUnplacedResults = lExistingUnplacedResults.filter(owner=request.user)
    
    if request.POST:
        lResultsSaved = []
        for field in request.POST.keys():
            if field.startswith('position-'):
                lSerial = field[len('position-'):]
                lValue = request.POST[field]
                if len(lValue) > 0:
                    if lValue.upper() == "W":
                        lValue = "10001"
                    elif lValue.upper() == "D":
                        lValue = "10000"
                    lMatchingResult = ContestResult.objects.filter(contest_event=lContestEvent, id=lSerial)[0]
                    lMatchingResult.results_position = lValue
                    lMatchingResult.lastChangedBy = request.user
                    if request.user.profile.enhanced_functionality or request.user.id == lMatchingResult.owner:
                        lMatchingResult.save()
            elif field.startswith('draw-'):
                lSerial = field[len('draw-'):]
                lValue = request.POST[field]
                if len(lValue) > 0:
                    lMatchingResult = ContestResult.objects.filter(contest_event=lContestEvent, id=lSerial)[0]
                    lMatchingResult.draw = lValue
                    lMatchingResult.lastChangedBy = request.user
                    if request.user.profile.enhanced_functionality or request.user.id == lMatchingResult.owner:
                        lMatchingResult.save()
            elif field.startswith('drawsecond-'):
                lSerial = field[len('drawsecond-'):]
                lValue = request.POST[field]
                if len(lValue) > 0:
                    lMatchingResult = ContestResult.objects.filter(contest_event=lContestEvent, id=lSerial)[0]
                    lMatchingResult.draw_second_part=lValue
                    lMatchingResult.lastChangedBy = request.user
                    if request.user.profile.enhanced_functionality or request.user.id == lMatchingResult.owner:
                        lMatchingResult.save()                
            elif field.startswith('points-'):
                lSerial = field[len('points-'):]
                lValue = request.POST[field]
                if len(lValue) > 0:
                    lMatchingResult = ContestResult.objects.filter(contest_event=lContestEvent, id=lSerial)[0]
                    lMatchingResult.points=lValue
                    lMatchingResult.lastChangedBy = request.user
                    if request.user.profile.enhanced_functionality or request.user.id == lMatchingResult.owner:
                        lMatchingResult.save()
            elif field.startswith('pointsfirst-'):
                lSerial = field[len('pointsfirst-'):]
                lValue = request.POST[field]
                if len(lValue) > 0:
                    lMatchingResult = ContestResult.objects.filter(contest_event=lContestEvent, id=lSerial)[0]
                    lMatchingResult.points_first_part=lValue
                    lMatchingResult.lastChangedBy = request.user
                    if request.user.profile.enhanced_functionality or request.user.id == lMatchingResult.owner:
                        lMatchingResult.save()
            elif field.startswith('pointssecond-'):
                lSerial = field[len('pointssecond-'):]
                lValue = request.POST[field]
                if len(lValue) > 0:
                    lMatchingResult = ContestResult.objects.filter(contest_event=lContestEvent, id=lSerial)[0]
                    lMatchingResult.points_second_part=lValue
                    lMatchingResult.lastChangedBy = request.user
                    if request.user.profile.enhanced_functionality or request.user.id == lMatchingResult.owner:
                        lMatchingResult.save()
            elif field.startswith('pointsthird-'):
                lSerial = field[len('pointsthird-'):]
                lValue = request.POST[field]
                if len(lValue) > 0:
                    lMatchingResult = ContestResult.objects.filter(contest_event=lContestEvent, id=lSerial)[0]
                    lMatchingResult.points_third_part=lValue
                    lMatchingResult.lastChangedBy = request.user
                    if request.user.profile.enhanced_functionality or request.user.id == lMatchingResult.owner:
                        lMatchingResult.save()
            elif field.startswith('pointsfourth-'):
                lSerial = field[len('pointsfourth-'):]
                lValue = request.POST[field]
                if len(lValue) > 0:
                    lMatchingResult = ContestResult.objects.filter(contest_event=lContestEvent, id=lSerial)[0]
                    lMatchingResult.points_fourth_part=lValue
                    lMatchingResult.lastChangedBy = request.user
                    if request.user.profile.enhanced_functionality or request.user.id == lMatchingResult.owner:
                        lMatchingResult.save()                             
            elif field.startswith('pointspenalty-'):
                lSerial = field[len('pointspenalty-'):]
                lValue = request.POST[field]
                if len(lValue) > 0:
                    if lValue.strip().startswith('-') == False:
                        lValue = "-%s" % lValue
                    lMatchingResult = ContestResult.objects.filter(contest_event=lContestEvent, id=lSerial)[0]
                    lMatchingResult.penalty_points=lValue
                    lMatchingResult.lastChangedBy = request.user
                    if request.user.profile.enhanced_functionality or request.user.id == lMatchingResult.owner:
                        lMatchingResult.save()    
            elif field.startswith('conductor-'):
                lSerial = field[len('conductor-'):]
                lValue = request.POST[field]
                if len(lValue) > 0:
                    lMatchingResult = ContestResult.objects.filter(contest_event=lContestEvent, id=lSerial)[0]
                    lMatchingPerson = Person.objects.filter(id=lValue)[0]
                    lMatchingResult.person_conducting=lMatchingPerson
                    lMatchingResult.lastChangedBy = request.user
                    if request.user.profile.enhanced_functionality or request.user.id == lMatchingResult.owner:
                        lMatchingResult.save()
            elif field.startswith('ownchoice-'):
                lSerial = field[len('ownchoice-'):]
                lValue = request.POST[field]
                if len(lValue) > 0:
                    lMatchingResult = ContestResult.objects.filter(contest_event=lContestEvent, id=lSerial)[0]
                    lMatchingPiece = TestPiece.objects.filter(id=lValue)[0]
                    lMatchingResult.test_piece=lMatchingPiece
                    lMatchingResult.lastChangedBy = request.user
                    if request.user.profile.enhanced_functionality or request.user.id == lMatchingResult.owner:
                        lMatchingResult.save()                        
                        
        lContestUrl = lContestEvent.get_absolute_url()
        lWinners = lContestEvent.winners()
        lWinnersTwitter = ""
        lAdditionalContext = {}
        for winner in lWinners:
            if winner.band.twitter_name:
                lWinnersTwitter += "@" + winner.band.twitter_name + " "
        lAdditionalContext["WinnersTwitter"] = lWinnersTwitter
        notification(None, lContestEvent, 'contests', 'contestevent', 'results_added', request.user, browser_details(request), pUrl=lContestUrl, pAdditionalContext=lAdditionalContext)
        return HttpResponseRedirect('/contests/%s/%s/' % (pContestSlug, pDate))

    return render_auth(request, 'addresults/amend_bands.html', {"Contest" : lContest,
                                                                "ContestEvent" : lContestEvent,
                                                                'ExistingUnplacedResults' : lExistingUnplacedResults,
                                                          })    


def _link_adjudicator(request, pOriginalAdjudicatorName, pContestEvent):
    """
    Link the passed adjudicator to the contest
    """
    lAdjudicatorName = pOriginalAdjudicatorName
    
    if lAdjudicatorName.lower() == 'unknown':
        return 
    
    # if it ends with a dot, remove it
    if lAdjudicatorName.endswith('.'):
        lAdjudicatorName = lAdjudicatorName[:-1]
    # if there is no space after a full stop then add one
    lAdjudicatorName = add_space_after_dot(lAdjudicatorName)
    # if there is no dot after an initial then add one
    lAdjudicatorName = add_dot_after_initial(lAdjudicatorName)
    # get rid of double spaces
    lAdjudicatorName = lAdjudicatorName.replace("  ", " ")
    
    lLastSpace = lAdjudicatorName.rfind(' ')
    if lLastSpace > 0:
        lAdjudicatorFirstNames = lAdjudicatorName[:lLastSpace].strip()
        lAdjudicatorSurname = lAdjudicatorName[lLastSpace:].strip()
    else:
        lAdjudicatorFirstNames = lAdjudicatorName
        lAdjudicatorSurname = lAdjudicatorName
        
    
    try:
        lPerson = Person.objects.filter(first_names__iexact=lAdjudicatorFirstNames, surname__iexact=lAdjudicatorSurname)[0]
    except IndexError:
        try:
            lPersonAlias = PersonAlias.objects.filter(name__iexact=lAdjudicatorName)[0]
            lPerson = lPersonAlias.person
        except IndexError:
            lPerson = Person()
            lPerson.surname = lAdjudicatorSurname
            lPerson.first_names = lAdjudicatorFirstNames
            lPerson.slug = slugify(lAdjudicatorName, instance=lPerson)
            lPerson.owner = request.user
            lPerson.lastChangedBy = request.user
            lPerson.save()
            notification(None, lPerson, 'people', 'person', 'new', request.user, browser_details(request))
            
    lContestAdjudicator = ContestAdjudicator()
    lContestAdjudicator.contest_event = pContestEvent
    lContestAdjudicator.adjudicator_name = lPerson.name
    lContestAdjudicator.person = lPerson
    lContestAdjudicator.owner = request.user
    lContestAdjudicator.lastChangedBy = request.user
    lContestAdjudicator.save()
    
    
@login_required
def enter_adjudicators(request, pContestSlug, pDate):
    """
    Enter the adjudicators for the contest
    """
    try:
        lContest = Contest.objects.filter(slug=pContestSlug)[0]
        lContestEvent = ContestEvent.objects.filter(contest=lContest, date_of_event=pDate)[0]
    except IndexError:
        raise Http404()
    
    if request.POST:
        lAdjudicatorName = request.POST['AdjudicatorName'].strip()
        if len(lAdjudicatorName) > 0:
            if lAdjudicatorName.find(',') == -1:
                _link_adjudicator(request, lAdjudicatorName, lContestEvent)
            else:
                lAdjudicators = lAdjudicatorName.split(',')
                for adjudicator in lAdjudicators:
                    _link_adjudicator(request, adjudicator.strip(), lContestEvent)        
            
        return HttpResponseRedirect('/addresults/%s/%s/6/' % (pContestSlug, pDate))
    else:
        
        lAdjudicatorNamesData = []
        
        cursor = connection.cursor()
        cursor.execute("select first_names || ' ' || surname || ' ' || coalesce (suffix, '') from people_person order by 1")
        rows = cursor.fetchall() 
        for row in rows:
            if row[0]: # causes error if row[0] is null, which seems happen sometimes!
                lAdjudicatorNamesData.append(row[0].strip())
        cursor.close()
            
        cursor = connection.cursor()
        cursor.execute("select name from people_personalias order by name")
        rows = cursor.fetchall() 
        for row in rows:
            lAdjudicatorNamesData.append(row[0])
        cursor.close()
            
        return render_auth(request, 'addresults/adjudicators.html', {"Contest" : lContest,
                                                                    "ContestEvent" : lContestEvent,
                                                                    "Data" : lAdjudicatorNamesData,
                                                                    })
@login_required      
def remove_adjudicator(request, pContestSlug, pDate, pContestAdjudicatorId):
    """
    Remove the link to an adjudicator
    """        
    try:
        lContestAdjudicator = ContestAdjudicator.objects.filter(id=pContestAdjudicatorId)[0]
    except IndexError:
        raise Http404()
    lContestAdjudicator.delete()
    return HttpResponseRedirect('/addresults/%s/%s/6/' % (pContestSlug, pDate))


@login_required     
def exists(request, pContestSlug, pDate):
    """
    There is already an existing contest of this type on that date
    """
    try:
        lContest = Contest.objects.filter(slug=pContestSlug)[0]
        lContestEvent = ContestEvent.objects.filter(contest=lContest, date_of_event=pDate)[0]
    except IndexError:
        raise Http404()
    return render_auth(request, 'addresults/exists.html', {"ContestEvent" : lContestEvent})


@login_required
def enter_notes(request, pContestSlug, pDate):
    """
    Enter any notes about the contest result
    """
    lForm = NotesForm()
    try:
        lContest = Contest.objects.filter(slug=pContestSlug)[0]
        lContestEvent = ContestEvent.objects.filter(contest=lContest, date_of_event=pDate)[0]
    except IndexError:
        raise Http404()
    
    # Process Notes
    if request.POST:
        lForm = NotesForm(request.POST)
        if lForm.is_valid():
            if lContestEvent.notes:
                lContestEvent.notes += "\n"
            lContestEvent.notes += lForm.cleaned_data['notes']
            lContestEvent.save() 
            return HttpResponseRedirect('/contests/%s/%s/' % (lContest.slug, lContestEvent.date_of_event))
        else:
            return HttpResponseRedirect('/contests/%s/%s/' % (lContest.slug, lContestEvent.date_of_event))
    else:
        lContestUrl = lContestEvent.get_absolute_url()
        lWinner = lContestEvent.winners()
        lAdditionalContext = {}
        for winner in lWinners:
            if winner.band.twitter_name:
                lWinnersTwitter += "@" + winner.band.twitter_name + " "
        lAdditionalContext["WinnersTwitter"] = lWinnersTwitter
        notification(None, lContestEvent, 'contests', 'contestevent', 'results_added', request.user, browser_details(request), pUrl=lContestUrl, pAdditionalContext=lAdditionalContext)
        return render_auth(request, 'addresults/notes.html', {"Contest" : lContest,
                                                              "ContestEvent" : lContestEvent,
                                                              "form" : lForm,
                                                             })
        
@login_required
def whitfriday(request):
    """
    Error message - trying to add a whit friday contest through normal means
    """
    return render_auth(request, 'addresults/whitfriday.html')

@login_required    
def rpc(request, pType):
    """
    Provide data for the popup
    """
    if request.POST:
        lQueryVar = request.POST['q']
        lType = 'html'
    else:
        lQueryVar = request.GET['q']
        lType = 'json'
    if pType == 'contest':
        lData = Contest.objects.filter(name__icontains=lQueryVar)
    if pType == 'testpiece':
        lData = TestPiece.objects.filter(name__icontains=lQueryVar)
    if pType == 'venue':
        lData = Venue.objects.filter(name__icontains=lQueryVar)
        
    return render_auth(request, 'addresults/rpc.%s' % lType, {'Data' : lData,
                                                              'Type' : pType,
                                                             })
        