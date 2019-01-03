# (c) 2019 Tim Sawyer, All Rights Reserved

from django.contrib.auth.decorators import login_required
from django.contrib.gis.geos import Point
from django.contrib.gis.measure import D
from django.http import Http404, HttpResponseRedirect

from bands.models import Band
from bbr.notification import notification
from bbr.siteutils import browser_details
from bbr.render import render_auth
from contests.models import ContestEvent, Venue
from bandmap.forms import EditLocationForm
from regions.models import Region
from django.conf import settings


def home(request):
    """
    Show google map of bands
    """
    return render_auth(request, 'map2/map.html', {'MapboxAccessToken': settings.MAPBOX_ACCESS_TOKEN})

def jsondata(request, pDataSlug):
    """
    Return geojson relating to the slug
    """
    lBands = Band.objects.all() # filter(region__name='Yorkshire')
    lBands = lBands.exclude(latitude="").exclude(latitude__isnull=True).exclude(longitude="").exclude(longitude__isnull=True).order_by('latitude', 'longitude')

    return render_auth(request, 'map2/section.json', {'Bands' : lBands})








def home_venues(request):
    """
    Show map of venues
    """
    return render_auth(request, 'map2/venues_map.html', {'GoogleMapsApiKey': settings.GOOGLE_MAPS_API_KEY})


def _get_map_search_parameters(request):
    """
    Get the map search parameters from the request
    """
    try:
        lLatitude = None
        lLatitudeString = request.GET.get('lat')
        if lLatitudeString and len(lLatitudeString) > 0:
            lLatitude = float(lLatitudeString)
            
        lLongitude = None
        lLongitudeString = request.GET.get('lng')
        if lLongitudeString and len(lLongitudeString) > 0:
            lLongitude = float(lLongitudeString)
        
        lDistance = None
        lMilesString = request.GET.get('distance')
        if lMilesString and len(lMilesString) > 0:
            lDistance = float(lMilesString)
        
        lType = request.GET.get('type')
        
        return lLatitude, lLongitude, lDistance, lType
    except ValueError:
        return (None,None,None,None)


def map_script(request):
    """
    Return the javascript to add markers for all the bands with a latitude and longitude
    Or if lat/lng passed as parameters, find bands within given distance miles of a point.  Return a map_script.js centered on that point, showing bands within 10 miles
    """
    lBands = Band.objects.exclude(latitude="").exclude(latitude__isnull=True).exclude(longitude="").exclude(longitude__isnull=True).order_by('latitude', 'longitude')
    return render_auth(request, 'map2/map_script.js', {
                                                      "Bands" : lBands,
                                                     })    

def map_script_search(request):
    """
    Return the javascript to add markers for bands within given distance miles of a point.  Return a map_script.js centered on that point, showing bands within 10 miles
    """
    lLatitude, lLongitude, lDistance, lType = _get_map_search_parameters(request)
    lVenues = None
    
    if lLatitude and lLongitude and lDistance:
        # showing map searched from a given lat/lng
        lSearchPoint = Point(lLongitude, lLatitude)
        lBands = Band.objects.distance(lSearchPoint).select_related('region').order_by('distance')
        if lType == 'km':
            lBands = lBands.filter(point__distance_lte=(lSearchPoint, D(km=lDistance))).exclude(status=0)
        else:
            lBands = lBands.filter(point__distance_lte=(lSearchPoint, D(mi=lDistance))).exclude(status=0)
            lType = 'mi'
    else:
        # showing full map
        lBands = []
        lVenues = []
    return render_auth(request, 'map2/map_script.js', {
                                                      "Bands" : lBands,
                                                      "Venues" : lVenues,
                                                      "Latitude" : lLatitude,
                                                      "Longitude" : lLongitude,
                                                      "Distance" : lDistance,
                                                      "ShowExtinct" : False,
                                                     })    

def search_map(request):
    """
    Search the map
    """
    lLatitude, lLongitude, lDistance, lType = _get_map_search_parameters(request)
    lLocation = ""
    if lDistance == None:
        lDistance = 10.0
        lLocation = "Leeds"
        
    lBands = None
    lBandsDrivingDistance = None
    lTypeDisplay = " miles"
    
    if lLatitude and lLongitude and lDistance:
        lShowDrivingDirections = request.GET.get('driving') == 'Y'
        lLocation = request.GET.get('location')
        lSearchPoint = Point(lLongitude, lLatitude)
        lBands = Band.objects.exclude(status=0).distance(lSearchPoint).select_related('region').order_by('distance')
        if lType == 'km':
            lBands = lBands.filter(point__distance_lte=(lSearchPoint, D(km=lDistance)))
            lTypeDisplay = "km"
        else:
            lBands = lBands.filter(point__distance_lte=(lSearchPoint, D(mi=lDistance)))
            lType = 'mi'
            lTypeDisplay = " miles"
         
        if lShowDrivingDirections:
            lBandsDrivingDistance = lBands[:25]
            
    try:
        lFrom = request.GET.get('from')
    except KeyError:
        lFrom = None
            
    return render_auth(request, 'map2/search_map.html', {
                                                        "Latitude" : lLatitude,
                                                        "Longitude" : lLongitude,
                                                        "Distance" : lDistance,
                                                        "Bands" : lBands,
                                                        "BandsDrivingDistance" : lBandsDrivingDistance,
                                                        "Location" : lLocation,
                                                        "Type" : lType,
                                                        "TypeDisplay" : lTypeDisplay,
                                                        "From" : lFrom,
                                                        "GoogleMapsApiKey" : settings.GOOGLE_MAPS_API_KEY
                                                       })    

@login_required
def add_band(request):
    """
    Add a band to the map
    """
    lBands = Band.objects.filter(latitude="")
    if request.POST:
        lBandSlug = request.POST['band']
        return HttpResponseRedirect('/map2/coordwrong/%s/' % lBandSlug)
    return render_auth(request, 'map2/addband.html', {"Bands" : lBands})

@login_required
def move_band(request):
    """
    Move a band already on the map, choose from a list of bands to change
    """
    if request.POST:
        lBandSlug = request.POST['band']
        return HttpResponseRedirect('/map2/coordwrong/%s/' % lBandSlug)
    lBands = Band.objects.exclude(latitude="")
    return render_auth(request, 'map2/moveband.html', {"Bands" : lBands})


@login_required
def move_specific_band(request, pBandSlug):
    """
    Move a band already on the map
    """
    try:
        lBand = Band.objects.filter(slug=pBandSlug)[0]
    except IndexError:
        raise Http404()
    lForm = EditLocationForm(instance=lBand)
    if request.POST:
        lForm = EditLocationForm(request.POST, instance=lBand)
        if lForm.is_valid():
            lOldBand = Band.objects.filter(id=lBand.id)[0]
            lNewBand = lForm.save(commit=False)
            lNewBand.lastChangedBy = request.user
            lNewBand.mapper = request.user
            lNewBand.save()
            notification(lOldBand, lNewBand, 'bands', 'band_map', 'move', request.user, browser_details(request))

            return HttpResponseRedirect('/map2/coordwrong/%s/saved/' % lBand.slug)
    return render_auth(request, 'map2/movespecificband.html', {"Band" : lBand,
                                                              "form" : lForm})
    
@login_required
def move_specific_band_done(request, pBandSlug):
    """
    Move complete
    """
    try:
        lBand = Band.objects.filter(slug=pBandSlug)[0]
    except IndexError:
        raise Http404()
    return render_auth(request, 'map2/movespecificbanddone.html', {"Band" : lBand })

def specific_band(request, pBandSlug):
    """
    Show the map centered on a particular band
    """
    try:
        lBand = Band.objects.filter(slug=pBandSlug)[0]
    except IndexError:
        raise Http404()
    
    lShowExtinct = False
    try:
        lShowExtinctParameter = request.GET['show_extinct']
        if lShowExtinctParameter == 'Y':
            lShowExtinct = True
    except KeyError:
        pass
    
    return render_auth(request, 'map2/map.html', {"Band" : lBand,
                                                 "ShowExtinct" : lShowExtinct })
    
def specific_venue(request, pVenueSlug):
    """
    Show the map centered on a particular venue
    """
    try:
        lVenue = Venue.objects.filter(slug=pVenueSlug)[0]
    except IndexError:
        raise Http404()
    
    return render_auth(request, 'map2/map.html', {"Venue" : lVenue,
                                                 "ShowExtinct" : False,
                                                 "ShowVenues" : True,
                                                })    

def specific_band_map_script(request, pBandSlug):
    """
    Return the javascript to add markers for all the bands with a postcode, centered on a specific band
    """
    try:
        lBand = Band.objects.filter(slug=pBandSlug)[0]
    except IndexError:
        raise Http404()
    lBands = Band.objects.exclude(latitude="").order_by('latitude', 'longitude')
    lVenues = Venue.objects.exclude(latitude="").order_by('latitude', 'longitude')
    return render_auth(request, 'map2/map_script.js', { "Bands" : lBands,
                                                       "Center" : lBand,
                                                       "Zoom" : "12",
                                                       "Venues" : lVenues,
                                                       "ShowExtinct" : False,
                                                     }) 
    
def specific_venue_map_script(request, pVenueSlug):
    """
    Return the javascript to add markers for all the bands with a postcode, centered on a specific venue
    """
    try:
        lVenue = Venue.objects.filter(slug=pVenueSlug)[0]
    except IndexError:
        raise Http404()
    lBands = Band.objects.exclude(latitude="").order_by('latitude', 'longitude')
    lVenues = Venue.objects.exclude(latitude="").order_by('latitude', 'longitude')
    return render_auth(request, 'map2/map_script.js', { "Bands" : lBands,
                                                       "Center" : lVenue,
                                                       "Zoom" : "12",
                                                       "Venues" : lVenues,
                                                       "ShowExtinct" : False,
                                                     })    
    
def specific_region_map_script(request, pRegionSlug):
    """
    Return the javascript to add markers for all the bands with a given region
    """
    try:
        lRegion = Region.objects.filter(slug=pRegionSlug)[0]
    except IndexError:
        raise Http404()
    
    lBands = Band.objects.exclude(latitude="").order_by('latitude', 'longitude').filter(region=lRegion)
    return render_auth(request, 'map2/map_script.js', { "Bands" : lBands,
                                                       "Center" : lRegion,
                                                       "Zoom" : lRegion.default_map_zoom,
                                                       "ShowExtinct" : True,
                                                     })          
    
def specific_contest_event_map_script(request, pContestEventId):
    """
    Return the javascript to add markers for all the bands at a particular contest, and the venue for that contest
    """
    try:
        lContestEvent = ContestEvent.objects.filter(id=pContestEventId).select_related('venue_link')[0]
    except IndexError:
        raise Http404()
    
    lVenue = lContestEvent.venue_link
    
    if lVenue == None:
        raise Http404
    
    if not (lVenue.latitude and lVenue.longitude):
        raise Http404
        
    lMaxDistance = 0
    lBandIds = []
    lResults = lContestEvent.contestresult_set.all().select_related('band')
    for result in lResults:
        lBandIds.append(result.band_id)
    lBands = Band.objects.filter(id__in=lBandIds).distance(lVenue.point).exclude(latitude__isnull=True, longitude__isnull=True).exclude(latitude='', longitude='')
    for lBand in lBands:
        if lBand.distance.mi > lMaxDistance:
            lMaxDistance = lBand.distance.mi
    lVenues = [lVenue,]

    lZoom = "8"    
    if lMaxDistance > 100:
        lZoom = "7"
    if lMaxDistance > 200:
        lZoom = "6"
    if lMaxDistance > 300:
        lZoom = "4"
    if lMaxDistance > 500:
        lZoom = "4"
    if lMaxDistance > 1000:
        lZoom = "3"
    if lMaxDistance > 4000:
        lZoom = "2"
    if lMaxDistance > 10000:
        lZoom = "1"
    
    return render_auth(request, 'map2/map_script.js', { "Bands" : lBands,
                                                       "Center" : lVenue,
                                                       "Zoom" : lZoom,
                                                       "Venues" : lVenues,
                                                       "ShowExtinct" : True,
                                                     })  
