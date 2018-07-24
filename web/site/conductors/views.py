# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved

from django.contrib.auth.decorators import login_required
from django.http.response import HttpResponsePermanentRedirect, Http404

from people.models import Person


def single_conductor(request, pConductorSlug):
    """
    Show details of a single conductor
    """
    return _show_single_conductor_page(request, pConductorSlug)


@login_required
def single_conductor_filter(request, pConductorSlug, pContestSlug):
    """
    Show single conductor page, filtered to a given contest
    """
    return _show_single_conductor_page(request, pConductorSlug, pContestFilterSlug=pContestSlug)


@login_required
def single_conductor_filter_group(request, pConductorSlug, pContestGroupSlug):
    """
    Show single conductor page, filtered to a given contest
    """
    return _show_single_conductor_page(request, pConductorSlug, pGroupFilterSlug=pContestGroupSlug)
    
    
@login_required
def single_conductor_filter_tag(request, pConductorSlug, pTagSlug):
    """
    Show details of a single conductor filtered to a specific contest tag
    """
    return _show_single_conductor_page(request, pConductorSlug, pFilterTagSlug=pTagSlug)
    
    
def _show_single_conductor_page(request, pConductorSlug, pContestFilterSlug=None, pGroupFilterSlug=None, pFilterTagSlug=None):
    """
    Show single conductor page
    """
    try:
        lPerson = Person.objects.filter(old_conductor_slug=pConductorSlug)[0]
    except IndexError:
        raise Http404
    
    return HttpResponsePermanentRedirect("/people/%s/" % lPerson.slug) 
    
