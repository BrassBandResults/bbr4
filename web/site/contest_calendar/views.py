# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from calendar import HTMLCalendar, monthrange, month_name
from datetime import date, datetime

from django.http import Http404
from django.http.response import HttpResponseRedirect
from django.utils.html import conditional_escape as esc
from django.utils.safestring import mark_safe

from bbr.decorators import login_required_pro_user
from bbr.render import render_auth
from contests.models import ContestEvent, ContestResult


class ContestCalendar(HTMLCalendar):

    def __init__(self, pContestEvents):
        super(ContestCalendar, self).__init__()
        self.contest_events = self.group_by_day(pContestEvents)

    def formatday(self, day, weekday):
        if day != 0:
            cssclass = self.cssclasses[weekday]
            if date.today() == date(self.year, self.month, day):
                cssclass += ' today'
            if day in self.contest_events:
                cssclass += ' filled'
                body = []
                for contest in self.contest_events[day]:
                    body.append('<a href="%s">' % contest.get_absolute_url())
                    body.append(esc(contest.contest.name))
                    body.append('</a><br/>')
                return self.day_cell(cssclass, '<div class="dayNumber">%d</div> %s' % (day, ''.join(body)))
            return self.day_cell(cssclass, '<div class="dayNumber">%d</div>' % day)
        return self.day_cell('noday', '&nbsp;')

    def formatmonth(self, year, month):
        self.year, self.month = year, month
        return super(ContestCalendar, self).formatmonth(year, month)

    def group_by_day(self, pContestEvents):
        lReturn = {}
        for event in pContestEvents:
            lDay = event.date_of_event.day
            try:
                lExistingEventsThatDay = lReturn[lDay]
            except KeyError:
                lExistingEventsThatDay = []
            lExistingEventsThatDay.append(event)
            lReturn[lDay] = lExistingEventsThatDay
        return lReturn 


    def day_cell(self, cssclass, body):
        return '<td class="%s">%s</td>' % (cssclass, body)


def home(request):
    """
    Show calendar of events this month
    """
    lToday = datetime.now()
    return calendar(request, lToday.year, lToday.month)

def named_month(month_num):
    return date(1900,month_num,1).strftime('%B')


def calendar(request, pYear, pMonth):
    """
    Show calendar of events for specified month and year
    """
    lYear = int(pYear)
    if lYear < 1800 or lYear > 2100:
        raise Http404
    lMonth = int(pMonth)
    try:
        lCalendarFromMonth = datetime(lYear, lMonth, 1)
    except ValueError:
        raise Http404
    lCalendarToMonth = datetime(lYear, lMonth, monthrange(lYear, lMonth)[1])
    lContestEvents = ContestEvent.objects.filter(date_of_event__gte=lCalendarFromMonth, date_of_event__lte=lCalendarToMonth).select_related('contest','contest__group')
    lContestEventsToShow = {}
    lContestEventsToShowAbove = {}
    lContestEventsToShowBelow = {}
    for lEvent in lContestEvents:
        if lEvent.contest.group:
            lGroup = lEvent.contest.group 
            lGroup.date_of_event = lEvent.date_of_event
            lGroup.contest = lEvent.contest
            lGroup.contest.name = lGroup.name
            lUniqueKey = "GROUP%s_%d" % (lGroup.actual_slug, lGroup.date_of_event.day)
            if lEvent.date_resolution == 'D':
                lContestEventsToShow[lUniqueKey] = lGroup
            elif lEvent.date_resolution == 'M':
                lContestEventsToShowAbove[lUniqueKey] = lGroup
            elif lEvent.date_resolution == 'Y':
                lContestEventsToShowBelow[lUniqueKey] = lGroup
        else:
            lUniqueKey = "EVENT%s_%d" % (lEvent.contest.slug, lEvent.date_of_event.day)
            if lEvent.date_resolution == 'D':
                lContestEventsToShow[lEvent.contest.slug] = lEvent
            elif lEvent.date_resolution == 'M':
                lContestEventsToShowAbove[lEvent.contest.slug] = lEvent
            elif lEvent.date_resolution == 'Y':
                lContestEventsToShowBelow[lEvent.contest.slug] = lEvent
            
    lCalendar = ContestCalendar(lContestEventsToShow.values()).formatmonth(lYear, lMonth)
    lPreviousYear = lYear
    lPreviousMonth = lMonth - 1
    if lPreviousMonth == 0:
        lPreviousMonth = 12
        lPreviousYear = lYear - 1
    lNextYear = lYear
    lNextMonth = lMonth + 1
    if lNextMonth == 13:
        lNextMonth = 1
        lNextYear = lYear + 1
    lYearAfterThis = lYear + 1
    lYearBeforeThis = lYear - 1
    
    return render_auth(request, 'calendar/home.html', {'Calendar' : mark_safe(lCalendar),
                                                       'Month' : lMonth,
                                                       'MonthName' : named_month(lMonth),
                                                       'Year' : lYear,
                                                       'PreviousMonth' : lPreviousMonth,
                                                       'PreviousMonthName' : named_month(lPreviousMonth),
                                                       'PreviousYear' : lPreviousYear,
                                                       'NextMonth' : lNextMonth,
                                                       'NextMonthName' : named_month(lNextMonth),
                                                       'NextYear' : lNextYear,
                                                       'YearBeforeThis' : lYearBeforeThis,
                                                       'YearAfterThis' : lYearAfterThis,
                                                       'ContestsThisMonth' : lContestEventsToShowAbove.values(),
                                                       'ContestsThisYear' : lContestEventsToShowBelow.values(),
                                                       })
    
    
@login_required_pro_user
def contests_for_year(request, pYear):
    """
    Show all contests for a particular year
    """
    return HttpResponseRedirect("/years/%d/" % int(pYear))


@login_required_pro_user
def contests_for_month(request, pYear, pMonth):
    """
    Show all contests for a particular month
    """
    lYear = int(pYear)
    lMonth = int (pMonth)
    lFirstDay = datetime(lYear, lMonth, 1)
    lLastDay = datetime(lYear, lMonth, monthrange(lYear, lMonth)[1])
    lEvents = ContestEvent.objects.filter(date_of_event__gte=lFirstDay,date_of_event__lte=lLastDay).order_by('date_of_event', 'contest__slug').select_related('contest')

    
    lWinners = ContestResult.objects.filter(contest_event__in=lEvents, results_position=1).select_related('band', 'person_conducting', 'band__region')
    for event in lEvents:  
        event.winners = []
        for winning_result in lWinners:
            if winning_result.contest_event_id == event.id:
                event.winners.append(winning_result)
                break
    
    return render_auth(request, 'calendar/month.html', {"Events" : lEvents,
                                                        "Year" : lYear,
                                                        "Month" : lMonth,
                                                        "MonthText" : month_name[lMonth],
                                                       })

@login_required_pro_user
def contests_for_day(request, pYear, pMonth, pDay):
    """
    Show all contests for a particular month
    """
    lYear = int(pYear)
    lMonth = int (pMonth)
    lDay = int(pDay)
    lDate = datetime(lYear, lMonth, lDay)
    lEvents = ContestEvent.objects.filter(date_of_event=lDate).order_by('date_of_event', 'contest__slug').select_related('contest')

    
    lWinners = ContestResult.objects.filter(contest_event__in=lEvents, results_position=1).select_related('band', 'person_conducting', 'band__region')
    for event in lEvents:  
        event.winners = []
        for winning_result in lWinners:
            if winning_result.contest_event_id == event.id:
                event.winners.append(winning_result)
                break
    
    return render_auth(request, 'calendar/day.html', {"Events" : lEvents,
                                                        "Year" : lYear,
                                                        "Month" : lMonth,
                                                        "MonthText" : month_name[lMonth],
                                                        "Day" : lDay,
                                                        "EventDate" : lDate,
                                                       })
