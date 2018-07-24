# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved



from django.db import connection
from django.http import Http404
from django.conf import settings
from django.db.models import Q

from bbr3.render import render_auth
from bbr3.decorators import login_required_pro_user

from bands.models import Band
from regions.models import Region

def region_list(request):
    """
    Show a list of a regions
    """
    cursor = connection.cursor()
    lResults = {}
    cursor.execute("select region_id, count(*) from bands_band group by region_id")
    rows = cursor.fetchall()
    for row in rows:
        lResults[row[0]] = row[1]
    cursor.close()
    
    lRegions = Region.objects.all()
    for region in lRegions:
        try:
            region.band_count = lResults[region.id]
        except KeyError:
            region.band_count = 0
        
    # add counts from sub regions
    lSubRegions = Region.objects.filter(container__isnull=False)
    for lSubRegion in lSubRegions:
        for lRegion in lRegions:
            if lRegion.id == lSubRegion.container.id:
                lRegion.band_count += lResults[lSubRegion.id]
                
            
    return render_auth(request, 'regions/regions.html', {"Regions" : lRegions})


@login_required_pro_user
def single_region(request, pRegionSlug):
    """
    Show details of a single region
    """
    try:
        lRegion = Region.objects.filter(slug=pRegionSlug).select_related()[0]
    except IndexError:
        raise Http404()
    
    # bands for this region 
    cursor = connection.cursor()
    lBandResults = {}
    cursor.execute("select band_id, count(*) from contests_contestresult group by band_id")
    rows = cursor.fetchall()
    for row in rows:
        lBandResults[row[0]] = row[1]
    cursor.close()
    
    lExtinctBandCount = 0
    lBands = []
    for band in lRegion.band_set.exclude(slug='0-select-a-band'):
        try:
            band.resultcount = lBandResults[band.id]
        except KeyError:
            band.resultcount= 0
        lBands.append(band)
        if band.status == 0:
            lExtinctBandCount += 1
    
    # contests for this region
    cursor = connection.cursor()
    lContestResults = {}
    cursor.execute("select contest_id, count(*) from contests_contestevent group by contest_id")
    rows = cursor.fetchall()
    for row in rows:
        lContestResults[row[0]] = row[1]
    cursor.close()
    
    lContests = []
    for contest in lRegion.contest_set.all():
        try:
            contest.resultcount = lContestResults[contest.id]
        except KeyError:
            contest.resultcount = 0
        lContests.append(contest)

    
    # bands and contests for any regions where this region is the parent
    lChildRegions = Region.objects.filter(container=lRegion)
    if len(lChildRegions) > 0:
        for region in lChildRegions:
            for band in region.band_set.all():
                try:
                    band.resultcount = lBandResults[band.id]
                except KeyError:
                    band.resultcount= 0
                lBands.append(band)
                if band.status == 0:
                    lExtinctBandCount += 1
            for contest in region.contest_set.all():
                try:
                    contest.resultcount = lContestResults[contest.id]
                except KeyError:
                    contest.resultcount = 0
                lContests.append(contest)    
    
    lRegion.bands = lBands
    lRegion.contests = lContests
        
    lAllRegions = Region.objects.filter(container__isnull=True)
    lAllUkRegions = Region.objects.filter(container__isnull=False)
    return render_auth(request, 'regions/region.html', {"Region" : lRegion,
                                                        "AllCountryRegions" : lAllRegions,
                                                        "AllUkRegions" : lAllUkRegions,
                                                        "BandCount" : len(lRegion.bands),
                                                        "ExtinctBandCount" : lExtinctBandCount, 
                                                        "GoogleMapsApiKey" : settings.GOOGLE_MAPS_API_KEY
                                                        })

@login_required_pro_user    
def region_links(request, pRegionSlug):
    """
    Show band links for a single region
    """
    try:
        lRegion = Region.objects.filter(slug=pRegionSlug).select_related()[0]
    except IndexError:
        raise Http404()
    
    lBaseList = Band.objects.filter(region=lRegion).exclude(status=0)

    lChampionshipSectionBands = lBaseList.filter(national_grading='Championship')
    lExcellenceSectionBands = lBaseList.filter(national_grading='Excellence')
    lEliteSectionBands = lBaseList.filter(national_grading='Elite')
    lAGradeBands = lBaseList.filter(national_grading='A Grade')
    lFirstSectionBands = lBaseList.filter(national_grading='First')
    lBGradeBands = lBaseList.filter(national_grading='B Grade')
    lSecondSectionBands = lBaseList.filter(national_grading='Second')
    lCGradeBands = lBaseList.filter(national_grading='C Grade')
    lThirdSectionBands = lBaseList.filter(national_grading='Third')
    lDGradeBands = lBaseList.filter(national_grading='D Grade')
    lFourthSectionBands = lBaseList.filter(national_grading='Fourth')
    lFifthSectionBands = lBaseList.filter(national_grading='Fifth')
    lYouthBands = lBaseList.filter(national_grading='Youth')
    lUngradedBands = lBaseList.filter(Q(national_grading__isnull=True)|Q(national_grading=''))


    return render_auth(request, 'regions/links.html', {"Region" : lRegion,
                                                        "ChampionshipBands" : lChampionshipSectionBands,
                                                        "ExcellenceBands" : lExcellenceSectionBands,
                                                        "EliteBands" : lEliteSectionBands,
                                                        "FirstSectionBands" : lFirstSectionBands,
                                                        "SecondSectionBands" : lSecondSectionBands,
                                                        "ThirdSectionBands" : lThirdSectionBands,
                                                        "FourthSectionBands" : lFourthSectionBands,
                                                        "FifthSectionBands" : lFifthSectionBands,
                                                        "YouthBands" : lYouthBands,
                                                        "AGradeBands" : lAGradeBands,
                                                        "BGradeBands" : lBGradeBands,
                                                        "CGradeBands" : lCGradeBands,
                                                        "DGradeBands" : lDGradeBands,
                                                        "UngradedBands" : lUngradedBands,
                                                        })