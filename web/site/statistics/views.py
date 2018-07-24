# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

import datetime
from random import randint

from django.contrib.auth.decorators import login_required
from django.db import connection

from people.models import Person
from bands.models import Band
from bbr3.decorators import login_required_pro_user
from bbr3.render import render_auth
from contests.models import Contest, ContestResult, ContestEvent, Venue
from pieces.models import TestPiece


def _bands_competed_last_year():
    """
    Count the bands that competed last year
    """
    lLastYear = datetime.datetime.now().year - 1
    cursor = connection.cursor()
    cursor.execute("SELECT count(distinct(r.band_id)) FROM contests_contestevent e, contests_contestresult r WHERE r.contest_event_id = e.id AND extract(year from e.date_of_event) = %(year)s GROUP BY extract(year from e.date_of_event) ORDER BY extract(year from e.date_of_event) desc", {'year' : lLastYear})
    rows = cursor.fetchall()
    lReturn = 0
    if rows and rows[0]:
        lReturn = rows[0][0]
    cursor.close()
    return lReturn

def _fetch_band_rehearsal_count(pAllBands, pDay):
    """
    Count the bands that rehearse on a specific day
    """
    lReturn = 0
    for band in pAllBands:
        if band.rehearsal_night_1 == pDay or band.rehearsal_night_2 == pDay:
            lReturn += 1
    return lReturn

@login_required_pro_user
def home(request):
    """
    Show site statistics
    """
    lBandCount = Band.objects.count()
    lLatestBand = Band.objects.all().order_by('-id')[0]
    lResultsCount = ContestResult.objects.count()
    lResultsWithPlacingsCount = ContestResult.objects.filter(results_position__gte=1, results_position__lte=9000).count()
    lEventsCount = ContestEvent.objects.count()
        
    lExtinctBands = Band.objects.filter(status=0).count()
    lContestCount = Contest.objects.count()
    lLatestContest = Contest.objects.all().order_by('-id')[0]
    lPeopleCount = Person.objects.count()
    lLatestPerson = Person.objects.all().order_by('-id')[0]
    lTestPieceCount = TestPiece.objects.count()
    lLatestTestPiece = TestPiece.objects.all().order_by('-id')[0]
    
    lWithWebsiteCount = Band.objects.filter(website__contains='.').count()
    lWebsiteCount = Band.objects.filter(website_review__gte=4).count()
    lRandomWebsite = Band.objects.filter(website_review__gte=4).all()[randint(0, lWebsiteCount-1)]
    lWebsiteUrl = lRandomWebsite.website
    lWebsiteName = lRandomWebsite.name
    
    lBandsCompetedLastYear = _bands_competed_last_year()
    
    lBandsMapped = 0
    cursor = connection.cursor()
    cursor.execute("SELECT count(*) FROM bands_band where length(longitude) > 0")
    rows = cursor.fetchall()
    if rows and rows[0]:
        lBandsMapped = rows[0][0]
    cursor.close()
    
    lExtinctBandsMapped = 0
    cursor = connection.cursor()
    cursor.execute("SELECT count(*) FROM bands_band where length(longitude) > 0 and status = 0")
    rows = cursor.fetchall()
    if rows and rows[0]:
        lExtinctBandsMapped = rows[0][0]
    cursor.close()
    
    lVenueCount = Venue.objects.all().count()
    lVenueMapCount = 0
    cursor = connection.cursor()
    cursor.execute("SELECT count(*) FROM contests_venue where length(longitude) > 0")
    rows = cursor.fetchall()
    if rows and rows[0]:
        lVenueMapCount = rows[0][0]
    cursor.close()
    
    lBands = Band.objects.exclude(rehearsal_night_1=None)
    lBandsWithRehearsalNightsCount = lBands.count()
    lMondayBandCount = _fetch_band_rehearsal_count(lBands, '1')
    lTuesdayBandCount = _fetch_band_rehearsal_count(lBands, '2')
    lWednesdayBandCount = _fetch_band_rehearsal_count(lBands, '3')
    lThursdayBandCount = _fetch_band_rehearsal_count(lBands, '4')
    lFridayBandCount = _fetch_band_rehearsal_count(lBands, '5')
    lSaturdayBandCount = _fetch_band_rehearsal_count(lBands, '6')
    lSundayBandCount = _fetch_band_rehearsal_count(lBands, '0')
    
    lMondayBandPercent = (lMondayBandCount * 100.0) / (lBandsWithRehearsalNightsCount * 100.0) * 100
    lTuesdayBandPercent = (lTuesdayBandCount * 100.0) / (lBandsWithRehearsalNightsCount * 100.0) * 100
    lWednesdayBandPercent = (lWednesdayBandCount * 100.0) / (lBandsWithRehearsalNightsCount * 100.0) * 100
    lThursdayBandPercent = (lThursdayBandCount * 100.0) / (lBandsWithRehearsalNightsCount * 100.0) * 100
    lFridayBandPercent = (lFridayBandCount * 100.0) / (lBandsWithRehearsalNightsCount * 100.0) * 100
    lSaturdayBandPercent = (lSaturdayBandCount * 100.0) / (lBandsWithRehearsalNightsCount * 100.0) * 100
    lSundayBandPercent = (lSundayBandCount * 100.0) / (lBandsWithRehearsalNightsCount * 100.0) * 100
    
    return render_auth(request, 'statistics/home.html', {
                                              'BandCount' : lBandCount,
                                              'LatestBand' : lLatestBand,
                                              'ResultsCount' : lResultsCount,
                                              'ResultsWithPlacingsCount' : lResultsWithPlacingsCount,
                                              'EventsCount' : lEventsCount,
                                              'ContestCount' : lContestCount,
                                              'LatestContest' : lLatestContest,
                                              'PeopleCount' : lPeopleCount,
                                              'LatestPerson' : lLatestPerson,
                                              'TestPieceCount' : lTestPieceCount,
                                              'LatestTestPiece' : lLatestTestPiece,
                                              'WithWebsiteCount' : lWithWebsiteCount,
                                              'BandsMapped' : lBandsMapped,
                                              'ExtinctBandsMapped' : lExtinctBandsMapped,
                                              'ExtinctBandsCount' : lExtinctBands, 
                                              'WebsiteUrl' : lWebsiteUrl,
                                              'WebsiteName' : lWebsiteName,
                                              'CompetedLastYear' : lBandsCompetedLastYear,
                                              'VenueCount' : lVenueCount,
                                              'VenueMapCount' : lVenueMapCount,
                                              'MondayBandCount' : lMondayBandCount,
                                              'TuesdayBandCount' : lTuesdayBandCount,
                                              'WednesdayBandCount' : lWednesdayBandCount,
                                              'ThursdayBandCount' : lThursdayBandCount,
                                              'FridayBandCount' : lFridayBandCount,
                                              'SaturdayBandCount' : lSaturdayBandCount,
                                              'SundayBandCount' : lSundayBandCount,
                                              
                                              'MondayBandPercent' : lMondayBandPercent,
                                              'TuesdayBandPercent' : lTuesdayBandPercent,
                                              'WednesdayBandPercent' : lWednesdayBandPercent,
                                              'ThursdayBandPercent' : lThursdayBandPercent,
                                              'FridayBandPercent' : lFridayBandPercent,
                                              'SaturdayBandPercent' : lSaturdayBandPercent,
                                              'SundayBandPercent' : lSundayBandPercent,
                                              
                                              })
