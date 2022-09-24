# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved



from datetime import date

from django.http import Http404

from bands.models import Band
from bbr.render import render_jsonp

def band_results(request, pBandSlug, pVersion):
    """
    Return the band's results as a JSONP script
    """
    try:
        lBand = Band.objects.filter(slug=pBandSlug).select_related()[0]
    except IndexError:
        raise Http404()
    
    try:
        lReferer = request.META['HTTP_REFERER']
    except KeyError:
        lReferer = ''
       
    lBandSlugUnderscore = pBandSlug.replace('-','_')
    lToday = date.today()
    lResults = lBand.contestresult_set.filter(contest_event__date_of_event__lte=lToday).select_related()
    return render_jsonp(request, 'embed/band_results.%d.jsonp' % int(pVersion), {"Band" : lBand,
                                                                           "ContestResults" : lResults,
                                                                           "BandSlugUnderscore" : lBandSlugUnderscore
                                                                          })
