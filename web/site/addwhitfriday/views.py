# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from datetime import date

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect
from django.utils.datastructures import MultiValueDictKeyError

from addwhitfriday.forms import ContestNameForm, ContestDateForm, \
    ResultsForm
from bands.models import Band, PreviousBandName
from bbr.siteutils import slugify
from bbr.render import render_auth    
from contests.models import ContestGroup
from regions.models import Region


@login_required
def enter_contest_name(request):
    """
    Select the contest we are entering results for - saddleworth or tameside
    """
    lForm = ContestNameForm()
    lContestName = ''
    if request.POST:
        lForm = ContestNameForm(request.POST)
        if lForm.is_valid():
            lContestGroup = lForm.cleaned_data['contest']
            return HttpResponseRedirect('/addwhitfriday/%s/' % lContestGroup.slug)
            
    return render_auth(request, 'addwhitfriday/contestname.html', {'form' : lForm })
    
    
@login_required    
def enter_contest_date(request, pContestSlug):
    """
    Enter date of contest
    """
    lContestDate = ""
    lForm = ContestDateForm()
    try:
        lContestGroup = ContestGroup.objects.filter(slug=pContestSlug)[0]
    except IndexError:
        raise Http404()
    if request.POST:
        lForm = ContestDateForm(request.POST)
        lContestDate = request.POST['ContestDate']
        if lForm.is_valid():
            lContestDate = lForm.cleaned_data['ContestDate']
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
            return HttpResponseRedirect('/addwhitfriday/%s/%s/' % (pContestSlug, lDate))
    return render_auth(request, 'addwhitfriday/contestdate.html', {"ContestGroup" : lContestGroup,
                                                                   "form" : lForm})
        
_BAND_PREFIX = "<ul class=\"errorlist\"><li>Can't find band '"
            
@login_required
def enter_results(request, pContestSlug, pDate):
    """
    Enter the actual results of the contest
    """
    lHowToCorrectErrors = ''
    lYear, lMonth, lDay = pDate.split('-')
    lContestDate = date(year=int(lYear), month=int(lMonth), day=int(lDay))
    try:
        lContestGroup = ContestGroup.objects.filter(slug=pContestSlug)[0]
    except IndexError:
        raise Http404()
    lForm = ResultsForm(lContestGroup)
    
    if request.POST:
        try:
            lRadioSelection = request.POST['band']
            if lRadioSelection == 'newband':
                # create a new band
                lNewBandName = request.POST['newbandname']
                lNewBand = Band()
                lNewBand.name = lNewBandName
                lNewBand.slug = slugify(lNewBandName, instance=lNewBand)
                lNewBand.region = Region.objects.filter(name='Unknown')[0]
                lNewBand.owner = request.user
                lNewBand.lastChangedBy = request.user
                lNewBand.save()
            elif lRadioSelection == 'nameonly':
                lPreviousBandName = request.POST['oldbandname']
                lBandSerial = request.POST['bandid']
                lBand = Band.objects.filter(id=int(lBandSerial))[0]
                lPreviousName = PreviousBandName()
                lPreviousName.old_name = lPreviousBandName
                lPreviousName.band = lBand
                lPreviousName.owner = request.user
                lPreviousName.lastChangedBy = request.user
                lPreviousName.save()
        except MultiValueDictKeyError:
            pass
        
        lForm = ResultsForm(lContestGroup, request.POST)
        if lForm.is_valid():
            lForm.save(request, lContestGroup, lContestDate)
            return HttpResponseRedirect('/contests/%s/' % lContestGroup.actual_slug)
        else:
            lFormErrors = str(lForm.errors['__all__'])
            if lFormErrors.startswith(_BAND_PREFIX):
                lBandName = lFormErrors[len(_BAND_PREFIX):-15]
                lBandDropList = '<select name="bandid">\n'
                lBands = Band.objects.all()
                for band in lBands:
                    lBandDropList = lBandDropList + '<option value="%s">%s</option>\n' % (band.id, band.name)
                lBandDropList = lBandDropList + '</select>'
                lHowToCorrectErrors = """You have two choices to fix this problem.  You can either create a new band, or assign this name as an old name of an already existing band.  Use existing bands where possible.<br/>
                                         <input type="radio" name="band" value="newband"/>Next submit will create a new band called: <input type="text" name="newbandname" value="%s"/><br/>
                                         <input type="radio" name="band" value="nameonly"/>Next submit will add a previous band name to %s called <b>%s</b><input type="hidden" name="oldbandname" value="%s"/><br/>
                                         <input type="radio" name="band" value="nothing" checked="checked"/>Do nothing, correct it in the text box below.
                                         """ % (lBandName, lBandDropList, lBandName, lBandName)
                                         
    
    return render_auth(request, 'addwhitfriday/bands.html', {"ContestGroup" : lContestGroup,
                                                             "ContestDate" : lContestDate,
                                                             "form" : lForm,
                                                             "HowToCorrectErrors" : lHowToCorrectErrors,
                                                             })