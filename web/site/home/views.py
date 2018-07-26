# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from django.shortcuts import render
from django.http import HttpResponse

import datetime
from random import randint

from django.db import connection

from bands.models import Band
from bbr.render import render_auth
from contests.models import ContestEvent
from contests.models import ContestResult
from home.models import FaqSection
from people.models import Person, ClassifiedPerson
from home.support import _fetch_this_week_in_history


def home(request):
    """
    Show homepage
    """
    lToday = datetime.date.today()
    lYesterday = lToday - datetime.timedelta(days=1)
    lTomorrow = lToday + datetime.timedelta(days=1)
    
    lLatestContests = ContestEvent.objects.all().order_by('-id')[:5]
    lFutureEvents = {}
    lFutureContestEvents = ContestEvent.objects.filter(date_of_event__gt=lTomorrow).order_by('date_of_event').select_related('contest', 'contest__group').exclude(no_contest=True)[:20]
    for event in lFutureContestEvents:
        if event.contest.group == None:
            event.contest_slug = event.contest.slug
            event.contest_name = event.contest.name
            lKey = str(event.date_of_event) + event.contest.slug
            lFutureEvents[lKey] = event
        else:
            event.contest_slug = event.contest.group.slug.upper()
            event.contest_name = event.contest.group.name
            lKey = str(event.date_of_event) + event.contest.group.slug
            lFutureEvents[lKey] = event
            
    lFutureEventDates = lFutureEvents.items()
    lFutureEventsSorted = [value for key, value in sorted(lFutureEventDates)]
    
    lEventsYesterday = ContestEvent.objects.filter(date_of_event=lYesterday).order_by('contest__group__id', 'contest__ordering').select_related('contest', 'contest__group').exclude(no_contest=True).filter(date_resolution='D')[:20]
    lEventsToday = ContestEvent.objects.filter(date_of_event=lToday).order_by('contest__group__id', 'contest__ordering').select_related('contest', 'contest__group').exclude(no_contest=True).filter(date_resolution='D')[:20]
    lEventsTomorrow = ContestEvent.objects.filter(date_of_event=lTomorrow).order_by('contest__group__id', 'contest__ordering').select_related('contest', 'contest__group').exclude(no_contest=True).filter(date_resolution='D')[:20]

    lRecentlyAdded = ContestEvent.objects.all().order_by('-id').select_related('contest', 'contest__group')[:24]
    lRecentResults = ContestEvent.objects.filter(date_of_event__lt=lYesterday).order_by('-date_of_event').select_related('contest', 'contest__group').exclude(no_contest=True)[:24]
        
    if len(lEventsYesterday) + len(lEventsToday) + len(lEventsTomorrow) == 0:
        lThisWeek = _fetch_this_week_in_history()
    else:
        lThisWeek = None
    
    # Get random person profile.
    lProfileRoot = ClassifiedPerson.objects.filter(visible=True, show_on_homepage=True)
    lProfileCount = lProfileRoot.count()
    lRandomProfile = None
    lSecondRandomProfile = None
    if lProfileCount > 0:
        lRandomProfile = lProfileRoot.all()[randint(0, lProfileCount-1)]
        if lProfileCount > 1:
            lSecondRandomProfile = lProfileRoot.exclude(id=lRandomProfile.id)[randint(0, lProfileCount-2)]
        
    return render_auth(request, 'home/home.html', {
                                              'LatestContests' : lLatestContests,
                                              'FutureEvents' : lFutureEventsSorted[:6],
                                              'RecentlyAdded' : lRecentlyAdded,
                                              'RecentResults' : lRecentResults,
                                              'RandomProfile' : lRandomProfile,
                                              'SecondRandomProfile' : lSecondRandomProfile,
                                              'ThisWeek' : lThisWeek,
                                              'EventsYesterday' : lEventsYesterday,
                                              'EventsToday' : lEventsToday,
                                              'EventsTomorrow' : lEventsTomorrow,
                                              })

def faq(request):
    """
    Show FAQ
    """
    lSections = FaqSection.objects.all()
    return render_auth(request, 'home/faq.html', {'Sections' : lSections})

def robotstxt(request):
    """
    Show robots.txt
    """
    return render_auth(request, 'robots.txt')

def about(request):
    """
    Show about us page
    """
    return render_auth(request, 'home/aboutus.html')

def cookies(request):
    """
    Show page with cookie details
    """
    return render_auth(request, 'home/cookies.html')

def sitemap_index(request):
    """
    Show sitemap index
    """
    lLatestPerson = Person.objects.all().order_by('-last_modified')[0]
    lPersonLastModified = lLatestPerson.last_modified
    lLatestBand = Band.objects.all().order_by('-last_modified')[0]
    lBandLastModified = lLatestBand.last_modified
    lLatestContestResult = ContestResult.objects.all().order_by('-last_modified')[0]
    lContestLastModified = lLatestContestResult.last_modified
    return render_auth(request, 'sitemap_index.txt', {
                                                      'BandLastModified':lBandLastModified,
                                                      'ContestLastModified':lContestLastModified,
                                                      'PersonLastModified':lPersonLastModified,
                                                     })
    