# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved

from django.http.response import HttpResponsePermanentRedirect, Http404

from people.models import Person


def single_adjudicator(request, pAdjudicatorSlug):
    """
    Show details for a single adjudicator
    """
    try:
        lPerson = Person.objects.filter(old_adjudicator_slug=pAdjudicatorSlug)[0]
    except IndexError:
        raise Http404
    
    return HttpResponsePermanentRedirect("/people/%s/" % lPerson.slug) 
