# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from bands.models import Band
from bbr.render import render_auth    
from regions.models import Region


def bands_english_active(request):
    """
    Return a JSON list of active English bands
    """
    lUkRegion = Region.objects.filter(slug='great-britain')[0]
    lEnglishRegions = Region.objects.filter(container=lUkRegion).exclude(slug='northern-ireland').exclude(slug='scotland').exclude(slug='wales')
    lBands = Band.objects.filter(region__in=lEnglishRegions).exclude(status=0).exclude(latitude__isnull=True).exclude(longitude__isnull=True).exclude(longitude='').exclude(latitude='').exclude(scratch_band=True)
    return render_auth(request, 'api/bands.json', {'Bands' : lBands})

def bands_english_none(request):
    """
    Return a JSON list of English Bands with no status
    """
    lUkRegion = Region.objects.filter(slug='great-britain')[0]
    lEnglishRegions = Region.objects.filter(container=lUkRegion).exclude(slug='northern-ireland').exclude(slug='scotland').exclude(slug='wales')
    lBands = Band.objects.filter(region__in=lEnglishRegions).filter(status__isnull=True).exclude(latitude__isnull=True).exclude(longitude__isnull=True).exclude(longitude='').exclude(latitude='').exclude(scratch_band=True)
    return render_auth(request, 'api/bands.json', {'Bands' : lBands})