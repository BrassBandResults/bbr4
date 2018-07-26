# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from datetime import datetime, date

from django.db import connection
from django.http.response import Http404

from bands.models import Band
from bbr.decorators import login_required_pro_user
from bbr.render import render_auth
from contests.models import ContestEvent, ContestResult
from regions.models import Region


class YearObject:
    pass


def year_list(request):
    """
    Show a list of years that have contests
    """
    cursor = connection.cursor()
    lYearObjects = []
    lThisYear = datetime.today().year
    cursor.execute("SELECT extract(year from e.date_of_event), count(distinct(r.band_id)), count(distinct(e.id)) FROM contests_contestevent e, contests_contestresult r WHERE r.contest_event_id = e.id GROUP BY extract(year from e.date_of_event) ORDER BY extract(year from e.date_of_event) desc ")
    rows = cursor.fetchall()
    for row in rows:
        lYearObject = YearObject()
        lYearObject.year = int(row[0])
        if lYearObject.year > lThisYear:
            continue
        lYearObject.competing_bands_count = row[1]
        lYearObject.contest_count = row[2]
        
        lYearObjects.append(lYearObject)
    cursor.close()
    
    lAllRegions = Region.objects.filter(container__isnull=True)
    lAllUkRegions = Region.objects.filter(container__isnull=False)
    return render_auth(request, 'years/years.html', {
                                                     "Years" : lYearObjects,
                                                     "AllCountryRegions" : lAllRegions,
                                                     "AllUkRegions" : lAllUkRegions,
                                                     })


@login_required_pro_user
def year_list_region(request, pRegionSlug):
    """
    Show a list of years that have contests for a given region
    """
    try:
        lRegion = Region.objects.filter(slug=pRegionSlug)[0]
    except IndexError:
        raise Http404
    
    lSql = 'SELECT extract(year from e.date_of_event) as "year", count(distinct(r.band_id)) as "bands", count(distinct(e.id)) as "contests" FROM contests_contestevent e INNER JOIN contests_contestresult r on  r.contest_event_id = e.id  INNER JOIN bands_band b on b.id = r.band_id INNER JOIN regions_region reg on reg.id = b.region_id WHERE reg.id = %d OR reg.container_id = %d GROUP BY extract(year from e.date_of_event)  ORDER BY 1 desc' % (lRegion.id, lRegion.id)
    
    cursor = connection.cursor()
    lYearObjects = {}
    lThisYear = datetime.today().year
    cursor.execute(lSql)
    rows = cursor.fetchall()
    for row in rows:
        lYear = str(row[0])[:4]
        lYearObject = YearObject()
        lYearObject.year = int(row[0])
        if lYearObject.year > lThisYear:
            continue
        lYearObject.competing_bands_count = row[1]
        lYearObject.contest_count = row[2]
        lYearObject.region_contest_count = 0
        
        lYearObjects[lYear] = lYearObject
    cursor.close()
    
    lSql = "SELECT extract(year from e.date_of_event), count(e.id) FROM contests_contestevent e INNER JOIN contests_venue v ON e.venue_link_id = v.id INNER JOIN regions_region r ON v.country_id = r.id WHERE r.id = %d OR r.container_id = %d GROUP BY extract(year from e.date_of_event) ORDER BY 1 asc" % (lRegion.id, lRegion.id)
    cursor = connection.cursor()
    cursor.execute(lSql)
    rows = cursor.fetchall()
    for row in rows:
        lYear = str(row[0])[:4]
        try:
            lYearObject = lYearObjects[lYear]
            lYearObject.region_contest_count = row[1]
        except KeyError:
            pass
    cursor.close() 
    
    lYearNumbers = lYearObjects.items()
    lYearNumbers = sorted(lYearNumbers)
    lYearNumbers.reverse()
    lYearsForPage = [value for key, value in lYearNumbers]
            
    return render_auth(request, 'years/years_region.html', {"Years" : lYearsForPage,
                                                            'Region' : lRegion})


@login_required_pro_user()
def single_year_region(request, pYear, pRegionSlug):
    """
    Show contests for a single year that involve bands from a specific region
    """
    return single_year(request, pYear, pRegionSlug)


@login_required_pro_user()
def single_year(request, pYear, pRegionSlug=None):
    """
    Show contests for a single year
    """
    lShowingYear = int(pYear)
    lThisYear = date.today().year
    
    lNextYear = lShowingYear + 1
    if lNextYear > lThisYear + 3:
        lNextYear = None
        
    lPreviousYear = lShowingYear - 1
    if lPreviousYear < 1845:
        lPreviousYear = None
    
    lRegion = None
    if pRegionSlug:
        # limit to region
        try:
            lRegion = Region.objects.filter(slug=pRegionSlug)[0]
        except IndexError:
            raise Http404
        lSql = "SELECT DISTINCT r.contest_event_id FROM contests_contestresult r INNER JOIN bands_band b ON b.id = r.band_id INNER JOIN regions_region reg ON reg.id = b.region_id INNER JOIN contests_contestevent e ON e.id = r.contest_event_id WHERE EXTRACT(year from e.date_of_event) = %s AND (reg.id = %d OR reg.container_id = %d) " % (lShowingYear, lRegion.id, lRegion.id)
        cursor = connection.cursor()
        cursor.execute(lSql)
        lEventSerials = []
        rows = cursor.fetchall()
        for row in rows:
            lEventSerials.append(int(row[0]))
        cursor.close()
        
        lEvents = ContestEvent.objects.filter(id__in=lEventSerials).order_by('date_of_event', 'contest__slug').select_related('contest')
    else:
        # all regions
        lFirstDay = datetime(int(pYear), 1, 1)
        lLastDay = datetime(int(pYear), 12, 31)
        lEvents = ContestEvent.objects.filter(date_of_event__gte=lFirstDay,date_of_event__lte=lLastDay).order_by('date_of_event', 'contest__slug').select_related('contest')
    
    lWinners = ContestResult.objects.filter(contest_event__in=lEvents, results_position=1).select_related('band', 'person_conducting', 'band__region')
    for event in lEvents:  
        event.winners = []
        for winning_result in lWinners:
            if winning_result.contest_event_id == event.id:
                event.winners.append(winning_result)
                break
    
    return render_auth(request, 'years/year.html', {"Events" : lEvents,
                                                    "Year" : pYear,
                                                    "NextYear" : lNextYear,
                                                    "PreviousYear" : lPreviousYear,
                                                    "Region" : lRegion,
                                                     })
