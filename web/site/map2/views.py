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

def jsondata(request, pDataSlug):
    """
    Return geojson relating to the slug
    """
    lBands = Band.objects.all().filter(national_grading=pDataSlug)
    lBands = lBands.exclude(latitude="").exclude(latitude__isnull=True).exclude(longitude="").exclude(longitude__isnull=True).order_by('latitude', 'longitude')

    return render_auth(request, 'map2/section.json', {'Bands' : lBands})
