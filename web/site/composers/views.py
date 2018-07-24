# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved
from django.http.response import Http404, HttpResponsePermanentRedirect

from people.models import Person


def single_composer(request, pComposerSlug):
    """
    Show details of a single composer
    """
    try:
        lPerson = Person.objects.filter(old_composer_slug=pComposerSlug)[0]
    except IndexError:
        raise Http404
    
    return HttpResponsePermanentRedirect("/people/%s/" % lPerson.slug) 

