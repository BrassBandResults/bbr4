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
    return render_auth(request, 'map2/map.html')

def jsonSection(request, pDataSlug):
    """
    Return geojson relating to the slug
    """
    lDataSlug = pDataSlug
    if lDataSlug == "A_grade": lDataSlug = 'A Grade'
    elif lDataSlug == "B_grade": lDataSlug = 'B Grade'
    elif lDataSlug == "C_grade": lDataSlug = 'C Grade'
    elif lDataSlug == "D_grade": lDataSlug = 'D Grade'
    lBands = Band.objects.all().filter(national_grading=lDataSlug)
    lBands = lBands.exclude(latitude="").exclude(latitude__isnull=True).exclude(longitude="").exclude(longitude__isnull=True).order_by('latitude', 'longitude')

    return render_auth(request, 'map2/section.json', {'Bands' : lBands})

def jsonStatus(request, pStatus):
    """
    Return geojson relating to a band status
    """
    lBands = Band.objects.all()
    if pStatus == 'Extinct':
        lBands = lBands.filter(status=0)
    elif pStatus == 'Non_competing':
        lBands = lBands.filter(status=2)
    elif pStatus == 'Youth':
        lBands = lBands.filter(status=3)
    elif pStatus == 'SA':
        lBands = lBands.filter(status=4)

    lBands = lBands.exclude(latitude="").exclude(latitude__isnull=True).exclude(longitude="").exclude(longitude__isnull=True).order_by('latitude', 'longitude')

    return render_auth(request, 'map2/section.json', {'Bands' : lBands})
