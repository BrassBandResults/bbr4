# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved



from datetime import date, timedelta
import re

from django.contrib.auth.decorators import login_required
from django.db import connection
from django.db.models import Q
from django.http import Http404, HttpResponseRedirect, HttpResponse
from django.template.loader import render_to_string
from django.utils.encoding import smart_text

from adjudicators.models import ContestAdjudicator
from bands.models import Band
from bbr.decorators import login_required_pro_user
from bbr.siteutils import slugify, browser_details
from bbr.render import render_auth
from contests.models import ContestResult, ContestGroup, Contest, ContestEvent
from people.forms import EditPersonForm, EditPersonAsSuperuserForm, EditClassifiedProfileForm
from people.models import Person, PersonAlias, ClassifiedPerson, PersonRelation
from bbr.notification import notification
from pieces.models import TestPiece
from tags.models import ContestTag
from users.models import PersonalContestHistory
import hashlib

def people_list(request):
    """
    Show list of people beginning with A
    """
    return people_list_filter_letter(request, 'A')

def people_list_filter_letter(request, pLetter):
    """
    Show a list of people starting with specified letter
    """
    lConducting = {}
    cursor = connection.cursor()
    cursor.execute("SELECT person_conducting_id, count(*) FROM contests_contestresult WHERE person_conducting_id IS NOT NULL AND results_position <= 10000 GROUP BY person_conducting_id")
    rows = cursor.fetchall()
    for row in rows:
        lConducting[row[0]] = row[1]
    cursor.close()

    cursor = connection.cursor()
    cursor.execute("SELECT second_person_conducting_id, count(*) FROM contests_contestresult WHERE second_person_conducting_id IS NOT NULL GROUP BY second_person_conducting_id")
    rows = cursor.fetchall()
    for row in rows:
        if row[0]:
            try:
                lExistingCount = lConducting[row[0]]
            except KeyError:
                lExistingCount = 0
            lConducting[row[0]] = lExistingCount + row[1]
    cursor.close()

    lWithdrawns = {}
    cursor = connection.cursor()
    cursor.execute("SELECT person_conducting_id, count(*) FROM contests_contestresult WHERE person_conducting_id IS NOT NULL AND results_position = 10001 GROUP BY person_conducting_id")
    rows = cursor.fetchall()
    for row in rows:
        lWithdrawns[row[0]] = row[1]
    cursor.close()

    lAdjudications = {}
    cursor = connection.cursor()
    cursor.execute("SELECT person_id, count(*) FROM adjudicators_contestadjudicator WHERE person_id IS NOT NULL GROUP BY person_id")
    rows = cursor.fetchall()
    for row in rows:
        lAdjudications[row[0]] = row[1]
    cursor.close()


    lCompositions = {}
    cursor = connection.cursor()
    cursor.execute("SELECT composer_id, count(*) FROM pieces_testpiece WHERE composer_id IS NOT NULL GROUP BY composer_id")
    rows = cursor.fetchall()
    for row in rows:
        lCompositions[row[0]] = row[1]
    cursor.close()

    lArrangements = {}
    cursor = connection.cursor()
    cursor.execute("SELECT arranger_id, count(*) FROM pieces_testpiece WHERE arranger_id IS NOT NULL GROUP BY  arranger_id")
    rows = cursor.fetchall()
    for row in rows:
        lArrangements[row[0]] = row[1]
    cursor.close()

    lComposerArranger = {}
    lComposerArranger.update(lCompositions)
    lComposerArranger.update(lArrangements)

    if pLetter == 'ALL':
        if request.user.is_authenticated() == False:
            raise Http404
        if request.user.profile.pro_member == False:
            raise Http404
        lPeople = Person.objects.all().exclude(slug="unknown")
    elif pLetter == 'NOTHING':
        lPeople = Person.objects.all().exclude(slug="unknown")
    else:
        lPeople = Person.objects.filter(surname__istartswith=pLetter).exclude(slug="unknown")

    for person in lPeople:
        try:
            person.conducting_count = lConducting[person.id]
        except KeyError:
            person.conducting_count = 0
        try:
            person.withdrawn_count = lWithdrawns[person.id]
        except KeyError:
            person.withdrawn_count = 0
        try:
            person.adjudications_count = lAdjudications[person.id]
        except KeyError:
            person.adjudications_count = 0
        try:
            person.composition_count = lCompositions[person.id]
        except KeyError:
            person.composition_count = 0
        try:
            person.arrangement_count = lArrangements[person.id]
        except KeyError:
            person.arrangement_count = 0

    if pLetter == 'NOTHING':
        lNothingPeople = []
        for person in lPeople:
            if person.conducting_count==0 and person.adjudications_count==0 and person.composition_count==0 and person.arrangement_count==0 and person.withdrawn_count == 0:
                lNothingPeople.append(person)
        lPeople = lNothingPeople

    lAllPeopleCount = Person.objects.all().count()

    lConductorsCheck = len(lConducting.keys())
    lAdjudicatorsCheck = len(lAdjudications.keys())
    lComposerArrangerCheck = len(lComposerArranger.keys())

    lVennAllCount = len(lConducting.keys() & lAdjudications.keys() & lComposerArranger.keys())
    lVennConductorAdjudicatorCount = len(lConducting.keys() & lAdjudications.keys()) - lVennAllCount
    lVennConductorComposerCount = len(lConducting.keys() & lComposerArranger.keys()) - lVennAllCount
    lVennComposerAdjudicatorCount = len(lAdjudications.keys() & lComposerArranger.keys()) - lVennAllCount
    lVennConductorOnlyCount = len(lConducting) - lVennConductorAdjudicatorCount - lVennConductorComposerCount - lVennAllCount
    lVennAdjudicatorOnlyCount = len(lAdjudications) - lVennComposerAdjudicatorCount - lVennConductorAdjudicatorCount - lVennAllCount
    lVennComposerArrangerOnlyCount = len(lComposerArranger) - lVennConductorComposerCount - lVennComposerAdjudicatorCount - lVennAllCount

    return render_auth(request, "people/people.html", {"People": lPeople,
                                                       "PeopleCount" : len(lPeople),
                                                       "AllPeopleCount" : lAllPeopleCount,
                                                       "StartsWith" : pLetter,
                                                       "VennAllCount" : lVennAllCount,
                                                       "VennConductorAdjudicatorCount" : lVennConductorAdjudicatorCount,
                                                       "VennConductorComposerCount" : lVennConductorComposerCount,
                                                       "VennComposerAdjudicatorCount" : lVennComposerAdjudicatorCount,
                                                       "VennConductorOnlyCount" : lVennConductorOnlyCount,
                                                       "VennAdjudicatorOnlyCount" : lVennAdjudicatorOnlyCount,
                                                       "VennComposerArrangerOnlyCount" : lVennComposerArrangerOnlyCount,
                                                       "ConductorsCheck" : lConductorsCheck,
                                                       "AdjudicatorsCheck" : lAdjudicatorsCheck,
                                                       "ComposerArrangerCheck" : lComposerArrangerCheck,
                                                      })


def _fetch_piece_details(pPerson):
    """
    Fetch composer/arranger details for this person
    """
    lComposedPieces = TestPiece.objects.filter(composer=pPerson)
    lArrangedPieces = TestPiece.objects.filter(arranger=pPerson)

    return (lComposedPieces, lArrangedPieces)

class ResultObject:
    pass

def _fetch_adjudication_details(pPerson):
    """
    Fetch adjudications performed by this person
    """
    cursor = connection.cursor()
    lAdjudications = []
    cursor.execute("""
SELECT event.date_of_event,
       event.name,
       contest.slug,
       result.band_name,
       (SELECT band.slug FROM bands_band band WHERE id = result.band_id),
       event.date_resolution,
       event.id
FROM contests_contestresult result
right outer join contests_contestevent event on (result.results_position = 1 and result.contest_event_id = event.id)
inner join contests_contest contest on contest.id = event.contest_id
WHERE event.id IN (SELECT adjudicator.contest_event_id
                   FROM adjudicators_contestadjudicator adjudicator
                   WHERE adjudicator.person_id = %d)
ORDER BY event.date_of_event desc
                   """ % pPerson.id)

    rows = cursor.fetchall()
    lContestEvent = ContestEvent()
    lPreviousResult = None
    for row in rows:
        result = ResultObject()
        result.date_of_event = row[0]
        result.event_name = row[1]
        result.contest_slug = row[2]
        result.band_name = row[3]
        result.band_slug = row[4]
        result.date_resolution = row[5]
        lContestEvent.date_of_event = result.date_of_event
        lContestEvent.date_resolution = result.date_resolution
        result.event_date = lContestEvent.event_date
        result.future = lContestEvent.future()
        lBand = Band()
        lBand.slug = result.band_slug
        lBand.name = result.band_name
        result.winners = [lBand,]
        result.contest_event_id = row[6]

        if lPreviousResult:
            if lPreviousResult.event_name == result.event_name and lPreviousResult.date_of_event == result.date_of_event:
                lPreviousResult.winners.append(lBand)
                continue

        lAdjudications.append(result)
        lPreviousResult = result
    cursor.close()

    return lAdjudications

def _fetch_conducting_details(pPerson, pContestFilterSlug, pGroupFilterSlug, pFilterTagSlug):
    """
    Fetch details of this person's conducting
    """
    lResults = ContestResult.objects.filter(Q(person_conducting=pPerson)|Q(second_person_conducting=pPerson)).select_related()
    lContestResults = lResults.exclude(contest_event__contest__group__group_type='W').exclude(results_position=10001) # Exclude withdrawn
    lThreeMonths = date.today() + timedelta(days=90)
    lContestResults = lContestResults.exclude(contest_event__date_of_event__gt=lThreeMonths) # Exclude more than 90 days in future
    lWhitFridayResults = lResults.filter(contest_event__contest__group__group_type='W')

    if pContestFilterSlug:
        lContest = Contest.objects.filter(slug=pContestFilterSlug)[0]
        lFiltered = True
        lFilteredTo = lContest
        lContestResults = lContestResults.filter(contest_event__contest=lContest)
        lWins = pPerson.wins.filter(contest_event__contest__slug=pContestFilterSlug).count()
        lSeconds = pPerson.seconds.filter(contest_event__contest__slug=pContestFilterSlug).count()
        lThirds = pPerson.thirds.filter(contest_event__contest__slug=pContestFilterSlug).count()
        lTopSixNotWin = pPerson.top_six_not_win.filter(contest_event__contest__slug=pContestFilterSlug).count()
        lUnplaced = pPerson.unplaced.filter(contest_event__contest__slug=pContestFilterSlug).count()
        lResultsWithPosition = pPerson.results_with_placings.filter(contest_event__contest__slug=pContestFilterSlug).count()


    elif pGroupFilterSlug:
        lGroup = ContestGroup.objects.filter(slug=pGroupFilterSlug.lower())[0]
        lFiltered = True
        lFilteredTo = lGroup
        lContestResults = lContestResults.filter(contest_event__contest__group=lGroup)
        lWins = pPerson.wins.filter(contest_event__contest__group__slug=pGroupFilterSlug).count()
        lSeconds = pPerson.seconds.filter(contest_event__contest__group__slug=pGroupFilterSlug).count()
        lThirds = pPerson.thirds.filter(contest_event__contest__group__slug=pGroupFilterSlug).count()
        lTopSixNotWin = pPerson.top_six_not_win.filter(contest_event__contest__group__slug=pGroupFilterSlug).count()
        lUnplaced = pPerson.unplaced.filter(contest_event__contest__group__slug=pGroupFilterSlug).count()
        lResultsWithPosition = pPerson.results_with_placings.filter(contest_event__contest__group__slug=pGroupFilterSlug).count()

    elif pFilterTagSlug:
        lContestTag = ContestTag.objects.filter(slug=pFilterTagSlug)[0]
        lFiltered = True
        lFilteredTo = lContestTag
        lFilteredResults = []
        lWins = 0
        lSeconds = 0
        lThirds = 0
        lTopSixNotWin = 0
        lUnplaced = 0
        lResultsWithPosition = 0
        for result in lContestResults:
            for tag in result.contest_event.tag_list():
                if lContestTag.id == tag.id:
                    lFilteredResults.append(result)
                    if result.results_position == 1:
                        lWins += 1
                    elif result.results_position == 2:
                        lSeconds += 1
                        lTopSixNotWin += 1
                    elif result.results_position == 3:
                        lThirds += 1
                        lTopSixNotWin += 1
                    elif result.results_position == 4:
                        lTopSixNotWin += 1
                    elif result.results_position == 5:
                        lTopSixNotWin += 1
                    elif result.results_position == 6:
                        lTopSixNotWin += 1
                    else:
                        lUnplaced += 1
                    if result.results_position < 8000:
                        lResultsWithPosition += 1
                    break
        lContestResults = lFilteredResults

    else:
        lFiltered = False
        lFilteredTo = None
        lWins = len(pPerson.wins)
        lSeconds = len(pPerson.seconds)
        lThirds = len(pPerson.thirds)
        lTopSixNotWin = len(pPerson.top_six_not_win)
        lUnplaced = len(pPerson.unplaced)
        lResultsWithPosition = len(pPerson.results_with_placings)

    return (lContestResults, lWhitFridayResults, lFiltered, lFilteredTo, lWins, lSeconds, lThirds, lTopSixNotWin, lUnplaced, lResultsWithPosition)


@login_required_pro_user
def single_person_filter_contest(request, pConductorSlug, pContestSlug):
    """
    Show single conductor page, filtered to a given contest
    """
    return single_person(request, pConductorSlug, pContestFilterSlug=pContestSlug)


@login_required_pro_user
def single_person_filter_group(request, pConductorSlug, pContestGroupSlug):
    """
    Show single conductor page, filtered to a given contest
    """
    return single_person(request, pConductorSlug, pGroupFilterSlug=pContestGroupSlug)


@login_required_pro_user
def single_person_filter_tag(request, pConductorSlug, pTagSlug):
    """
    Show details of a single conductor filtered to a specific contest tag
    """
    return single_person(request, pConductorSlug, pFilterTagSlug=pTagSlug)



def single_person(request, pPersonSlug, pContestFilterSlug=None, pGroupFilterSlug=None, pFilterTagSlug=None):
    """
    Show details of a single person
    """
    if pPersonSlug == 'unknown':
        raise Http404()

    if pContestFilterSlug or pGroupFilterSlug or pFilterTagSlug:
        if request.user.profile.pro_member == False:
            raise Http404()

    try:
        lPerson = Person.objects.filter(slug=pPersonSlug)[0]
        lPersonAliases = PersonAlias.objects.filter(person=lPerson).exclude(hidden=True)
    except IndexError:
        raise Http404()

    lComposedPieces, lArrangedPieces = _fetch_piece_details(lPerson)
    lAdjudications = _fetch_adjudication_details(lPerson)
    lContestResults, lWhitFridayResults, lFiltered, lFilteredTo, lWins, lSeconds, lThirds, lTopSixNotWin, lUnplaced, lResultsWithPosition = _fetch_conducting_details(lPerson, pContestFilterSlug, pGroupFilterSlug, pFilterTagSlug)

    lArraysWithEntries = 0
    if len(lComposedPieces) > 0:
        lArraysWithEntries += 1
    if len(lArrangedPieces) > 0:
        lArraysWithEntries += 1
    if len(lAdjudications) > 0:
        lArraysWithEntries += 1
    if len(lContestResults) > 0:
        lArraysWithEntries += 1
    if len(lWhitFridayResults) > 0:
        lArraysWithEntries += 1

    if lArraysWithEntries > 1:
        lShowTabs = True
    else:
        lShowTabs = False

    lShowEdit = False
    if request.user.is_anonymous() == False:
        lShowEdit = request.user.profile.superuser or (request.user.profile.enhanced_functionality and request.user.id == lPerson.owner.id)

    try:
        lClassifiedProfile = ClassifiedPerson.objects.filter(person=lPerson,visible=True)[0]
    except IndexError:
        lClassifiedProfile = None

    lFirstResultYear = None
    if lPerson.earliest_result():
        lFirstResultYear = lPerson.earliest_result().contest_event.date_of_event.year
    lLastResultYear = None
    if lPerson.latest_result():
        lLastResultYear = lPerson.latest_result().contest_event.date_of_event.year

    lUserResultsForThisAdjudicator = []
    if request.user.is_anonymous == False and len(lAdjudications) > 0 and request.user.profile.pro_member:
        # find this users adjudications by this person from their contest history
        lContestEvents = []

        # Get list of contest events adjudicated
        lContestAdjudications = ContestAdjudicator.objects.filter(person=lPerson).select_related('contest_event')
        for lContestAdjudication in lContestAdjudications:
            lContestEvents.append(lContestAdjudication.contest_event)

        lUserResultsForThisAdjudicatorWithDate = []
        lUserHistoryThisPiece = PersonalContestHistory.objects.filter(user=request.user, status='accepted', result__contest_event__in=lContestEvents).select_related('result', 'result__band', 'result__contest_event', 'result__contest_event__contest')
        if len(lUserHistoryThisPiece):
            for lUserHistory in lUserHistoryThisPiece:
                lUserResultsForThisAdjudicatorWithDate.append((lUserHistory.result.contest_event.date_of_event, lUserHistory.result))

        for result in lUserResultsForThisAdjudicatorWithDate:
            lUserResultsForThisAdjudicator.append(result[1])

    lRelationsOut = PersonRelation.objects.filter(source_person=lPerson)
    lRelationsBack = PersonRelation.objects.filter(relation_person=lPerson)

    return render_auth(request, 'people/person.html', {"Person" : lPerson,
                                                       "ContestResults" : lContestResults,
                                                       "WhitFridayResults" : lWhitFridayResults,
                                                       "ContestResultsCount" : len(lContestResults),
                                                       "WhitFridayResultsCount" : len(lWhitFridayResults),
                                                       "Profile" : lClassifiedProfile,
                                                       "Adjudications" : lAdjudications,
                                                       "AdjudicationsCount" : len(lAdjudications),
                                                       "ShowTabs" : lShowTabs,
                                                       "ComposedPieces" : lComposedPieces,
                                                       "ArrangedPieces" : lArrangedPieces,
                                                       "ComposedPiecesCount" : len(lComposedPieces),
                                                       "ArrangedPiecesCount" : len(lArrangedPieces),
                                                       "Filter" : lFiltered,
                                                       "FilteredTo" : lFilteredTo,
                                                       "ShowEdit" : lShowEdit,
                                                       "FirstResultYear" : lFirstResultYear,
                                                       "LastResultYear" : lLastResultYear,
                                                       "Wins": lWins,
                                                       "Seconds": lSeconds,
                                                       "Thirds": lThirds,
                                                       "TopSixNotWin": lTopSixNotWin,
                                                       "Unplaced": lUnplaced,
                                                       "ResultsWithPosition" : lResultsWithPosition,
                                                       "Aliases" : lPersonAliases,
                                                       "UserAdjudications" : lUserResultsForThisAdjudicator,
                                                       "UserAdjudicationsCount" : len(lUserResultsForThisAdjudicator),
                                                       "RelationsOut" : lRelationsOut,
                                                       "RelationsBack" : lRelationsBack,
                                                })

@login_required
def people_options(request):
    """
    Return <option> tags for droplist of people
    """
    try:
        lExclude = request.GET['exclude']
        lPeople = Person.objects.exclude(id=lExclude)
    except KeyError:
        lPeople = Person.objects.all()

    return render_auth(request, 'people/option_list.htm', {"People" : lPeople})

@login_required
def people_options_json(request):
    """
    Return <option> tags for droplist of people
    """
    lPeople = Person.objects.all()
    return render_auth(request, 'people/option_list.json', {"People" : lPeople})


@login_required
def add_person(request):
    """
    Add a new person
    """
    lFormType = EditPersonForm
    if request.user.profile.superuser:
        lFormType = EditPersonAsSuperuserForm
    if request.user.profile.superuser == False:
        if request.user.profile.enhanced_functionality == False:
            raise Http404()
    if request.method == 'POST':
        form = lFormType(request.POST)
        if form.is_valid():
            lNewPerson = form.save(commit=False)
            lNewPerson.slug = slugify(lNewPerson.name, instance=lNewPerson)
            lNewPerson.lastChangedBy = request.user
            lNewPerson.owner = request.user
            lNewPerson.save()

            notification(None, lNewPerson, 'people', 'person', 'new', request.user, browser_details(request))

            return HttpResponseRedirect('/people/')
    else:
        form = lFormType()

    return render_auth(request, 'people/new_person.html', {'form': form})


@login_required
def edit_person(request, pPersonSlug):
    """
    Edit a person
    """
    try:
        lPerson = Person.objects.filter(slug=pPersonSlug)[0]
    except IndexError:
        raise Http404()
    lFormType = EditPersonForm
    if request.user.profile.superuser:
        lFormType = EditPersonAsSuperuserForm
    if request.user.profile.superuser == False:
        if request.user.id != lPerson.owner.id:
            raise Http404()
        if request.user.profile.enhanced_functionality == False:
            raise Http404()
    if request.method == 'POST':
        form = lFormType(request.POST, instance=lPerson)
        if form.is_valid():
            lOriginalPerson = Person.objects.filter(id=lPerson.id)[0]

            lNewPerson = form.save(commit=False)
            lNewPerson.lastChangedBy = request.user
            lNewPerson.save()

            notification(lOriginalPerson, lNewPerson, 'people', 'person', 'edit', request.user, browser_details(request))

            return HttpResponseRedirect('/people/%s/' % lPerson.slug)
    else:
        form = lFormType(instance=lPerson)

    return render_auth(request, 'people/edit_person.html', {'form': form, "Person" : lPerson})


@login_required
def single_person_aliases(request, pPersonSlug):
    """
    Show and edit aliases for a given person
    """
    if pPersonSlug == 'unknown':
        raise Http404()

    if request.user.profile.superuser == False:
        raise Http404()

    try:
        lPerson = Person.objects.filter(slug=pPersonSlug)[0]
    except IndexError:
        raise Http404()

    if request.POST:
        lNewAlias = request.POST['new_alias_name']
        lPersonAlias = PersonAlias()
        lPersonAlias.person = lPerson
        lPersonAlias.name = lNewAlias
        lPersonAlias.owner = request.user
        lPersonAlias.lastChangedBy = request.user
        lPersonAlias.save()
        notification(None, lPersonAlias, 'people', 'person_alias', 'new', request.user, browser_details(request))
        return HttpResponseRedirect('/people/%s/aliases/' % lPerson.slug)

    lPeopleAliases = PersonAlias.objects.filter(person=lPerson)

    return render_auth(request, "people/person_aliases.html", {
                                                                     'Person' : lPerson,
                                                                     'Aliases' : lPeopleAliases,
                                                                     })


@login_required
def single_person_alias_show(request, pPersonSlug, pAliasSerial):
    """
    Show an alias on the pseron page
    """
    if request.user.profile.superuser == False:
        raise Http404()

    try:
        lPersonAlias = PersonAlias.objects.filter(person__slug=pPersonSlug, id=pAliasSerial)[0]
    except IndexError:
        raise Http404

    lPersonAlias.hidden = False
    lPersonAlias.lastChangedBy = request.user
    lPersonAlias.save()
    notification(None, lPersonAlias, 'people', 'person_alias', 'show', request.user, browser_details(request))
    return HttpResponseRedirect('/people/%s/aliases/' % pPersonSlug)


@login_required
def single_person_alias_hide(request, pPersonSlug, pAliasSerial):
    """
    Hide an alias on the person page
    """
    if request.user.profile.superuser == False:
        raise Http404()

    try:
        lPersonAlias = PersonAlias.objects.filter(person__slug=pPersonSlug, id=pAliasSerial)[0]
    except IndexError:
        raise Http404

    lPersonAlias.hidden = True
    lPersonAlias.lastChangedBy = request.user
    lPersonAlias.save()
    notification(None, lPersonAlias, 'people', 'person_alias', 'hide', request.user, browser_details(request))
    return HttpResponseRedirect('/people/%s/aliases/' % pPersonSlug)


@login_required
def single_person_alias_delete(request, pPersonSlug, pAliasSerial):
    """
    Delete a conductor alias
    """
    if request.user.profile.superuser == False:
        raise Http404()

    try:
        lPersonAlias = PersonAlias.objects.filter(person__slug=pPersonSlug, id=pAliasSerial)[0]
    except IndexError:
        raise Http404

    notification(None, lPersonAlias, 'people', 'person_alias', 'delete', request.user, browser_details(request))
    lPersonAlias.delete()
    return HttpResponseRedirect('/people/%s/aliases/' % pPersonSlug)


@login_required_pro_user
def single_person_csv(request, pPersonSlug):
    """
    Csv file of results for a conductor
    """
    try:
        lPerson = Person.objects.filter(slug=pPersonSlug)[0]
    except IndexError:
        raise Http404()

    lResults = ContestResult.objects.filter(Q(person_conducting=lPerson)|Q(second_person_conducting=lPerson)).select_related()
    lContestResults = lResults.exclude(contest_event__contest__group__group_type='W').exclude(results_position=10001)
    lWhitFridayResults = lResults.filter(contest_event__contest__group__group_type='W')

    lCsvFile = render_to_string('people/results.csv', {"Person" : lPerson,
                                                       "ContestResults" : lContestResults,
                                                       "WhitFridayResults" : lWhitFridayResults,
                                                       })

    lResponse = HttpResponse(content_type="text/csv")
    lResponse['Content-Disposition'] = "attachment; filename=%s.csv" % lPerson.slug
    lResponse.write(lCsvFile)
    return lResponse

@login_required_pro_user
def new_classified(request, pPersonSlug):
    """
    Create a new classified entry for this person
    """
    try:
        lPerson = Person.objects.filter(slug=pPersonSlug)[0]
    except IndexError:
        raise Http404

    if request.user.is_anonymous == True or request.user.profile.pro_member == False:
        raise Http404

    lMaxProfiles = request.user.profile.max_profile_count
    lActualPeopleProfilesCount = ClassifiedPerson.objects.filter(owner=request.user).count()

    if (lActualPeopleProfilesCount >= lMaxProfiles):
        return HttpResponseRedirect("/people/%s/newclassified/too_many/?username=%s" % (lPerson.slug,request.user.username))

    lProfile = None
    try:
        lProfile = ClassifiedPerson.objects.filter(person=lPerson)[0]
    except IndexError:
        lProfile = None

    if request.method == 'POST':
        if lProfile:
            if lProfile.owner != request.user:
                raise Http404
            lForm = EditClassifiedProfileForm(request.POST, instance=lProfile)
        else:
            lForm = EditClassifiedProfileForm(request.POST)
        if lForm.is_valid():
            # save new profile
            lNewProfile = lForm.save(commit=False)
            lNewProfile.person = lPerson
            lNewProfile.lastChangedBy = request.user
            lNewProfile.owner = request.user
            lNewProfile.visible = True
            lNewProfile.show_on_homepage = False
            lNewProfile.save()

            # email notification
            notification(None, lNewProfile, 'people', 'profile', 'new', request.user, browser_details(request))

            # redirect to person page
            return HttpResponseRedirect('/people/%s/' % pPersonSlug)
    else:
        if lProfile:
            lForm = EditClassifiedProfileForm(instance=lProfile)
        else:
            lForm = EditClassifiedProfileForm()

    return render_auth(request, 'people/edit_classified.html', {"Person" : lPerson,
                                                                "form" : lForm,
                                                               })

@login_required_pro_user
def edit_classified(request, pPersonSlug):
    """
    Edit a classified entry for this person
    """
    try:
        lPerson = Person.objects.filter(slug=pPersonSlug)[0]
    except IndexError:
        raise Http404

    if request.user.is_anonymous == True or request.user.profile.pro_member == False:
        raise Http404

    lProfile = None
    try:
        lProfile = ClassifiedPerson.objects.filter(person=lPerson)[0]
    except IndexError:
        lProfile = None

    if request.method == 'POST':
        if lProfile:
            if lProfile.owner != request.user:
                raise Http404
            lForm = EditClassifiedProfileForm(request.POST, instance=lProfile)
        else:
            lForm = EditClassifiedProfileForm(request.POST)
        if lForm.is_valid():
            # save new profile
            lNewProfile = lForm.save(commit=False)
            lNewProfile.person = lPerson
            lNewProfile.lastChangedBy = request.user
            lNewProfile.owner = request.user
            lNewProfile.save()

            # email notification
            notification(None, lNewProfile, 'people', 'profile', 'edit', request.user, browser_details(request))

            # redirect to person page
            return HttpResponseRedirect('/people/%s/' % pPersonSlug)
    else:
        if lProfile:
            lForm = EditClassifiedProfileForm(instance=lProfile)
        else:
            lForm = EditClassifiedProfileForm()

    return render_auth(request, 'people/edit_classified.html', {"Person" : lPerson,
                                                                "form" : lForm,
                                                               })

@login_required_pro_user
def too_many_classified(request, pPersonSlug):
    """
    User already has profiles
    """
    lPeople = ClassifiedPerson.objects.filter(owner=request.user)

    return render_auth(request, 'people/too_many_classified.html', {
                                                                    'Classifieds': lPeople,
                                                                    })


def chart_json(request, pPersonSlug):
    """
    Get the json to show the chart for a conductor
    """
    try:
        lPerson = Person.objects.filter(slug=pPersonSlug)[0]
    except IndexError:
        raise Http404()
    return render_auth(request, 'bands/resultschart.json', {"Results" : lPerson.reverse_results(),
                                                            "ShowBand" : True,
                                                            "ShowConductor" : False})


def chart_json_filter(request, pPersonSlug, pContestSlug):
    """
    Get the json to show the chart for a conductor, filtered by contest
    """
    try:
        lPerson = Person.objects.filter(slug=pPersonSlug)[0]
    except IndexError:
        raise Http404()
    return render_auth(request, 'bands/resultschart.json', {"Results" : lPerson.reverse_results(pContestSlug),
                                                            "ShowBand" : False,
                                                            "ShowConductor" : True})


def chart_json_filter_group(request, pPersonSlug, pContestGroupSlug):
    """
    Get the json to show the chart for a conductor, filtered by contest group
    """
    try:
        lPerson = Person.objects.filter(slug=pPersonSlug)[0]
    except IndexError:
        raise Http404()
    return render_auth(request, 'bands/resultschart.json', {"Results" : lPerson.reverse_results(pContestGroupSlug),
                                                            "ShowBand" : False,
                                                            "ShowConductor" : True})

def about_profile(request):
    """
    How to get your own profile
    """
    return render_auth(request, 'people/about_profile.html')



def people_hash_by_letter(request):
    """
    Return the people list hashes, one for the first letter by surname
    """
    lPeople = Person.objects.all().order_by('surname');
    lPeopleStructure = {}
    for person in lPeople:
        if person.surname:
            lFirstLetter = person.surname[0].upper()
            if lFirstLetter:
                try:
                    lList = lPeopleStructure[lFirstLetter]
                except KeyError:
                    lList = u""
                lList += u"!" + smart_text(person.first_names) + u"," + smart_text(person.surname);
                lPeopleStructure[lFirstLetter] = lList

    lHashes = {}

    for letter in lPeopleStructure.keys():
        lPeople = lPeopleStructure[letter]
        lHash = hashlib.sha256(lPeople.encode('utf-8')).hexdigest()
        lHashes[letter] = lHash

    return render_auth(request, 'people/hashes.json', {
                                                       'Hashes' : lHashes,
                                                       })

@login_required
def people_list_by_letter(request, pLetter):
    """
    Return JSON representing people starting with a certain letter
    """
    lPeople = Person.objects.filter(surname__istartswith=pLetter)
    return render_auth(request, 'people/people.json', {
                                                       'People' : lPeople,
                                                       })


@login_required_pro_user
def number_bands(request):
    """
    Show list of which conductors have taken the most bands
    """
    lPeople = []
    cursor = connection.cursor()

    cursor.execute("""
WITH bands AS (
  SELECT r.person_conducting_id, count(distinct r.band_id) as bandcount
  FROM contests_contestresult r
  GROUP BY r.person_conducting_id
  ORDER BY 2 desc
)
SELECT p.slug, p.surname, p.first_names, b.bandcount
FROM people_person p
INNER JOIN bands b ON b.person_conducting_id = p.id
WHERE b.bandcount > 4
AND b.person_conducting_id != 310730 -- unknown
ORDER BY 4 desc
    """)

    rows = cursor.fetchall()
    for row in rows:
        lPerson = ResultObject()
        lPerson.slug = row[0]
        lPerson.surname = row[1]
        lPerson.first_names = row[2]
        lPerson.bandcount = row[3]
        lPeople.append(lPerson)
    cursor.close()
    return render_auth(request, 'people/bandcount.html', {
                                                       'People' : lPeople,
                                                       })
@login_required_pro_user
def contest_winners(request):
    """
    Show list of which conductors have won the most contests, excluding whit friday
    """
    lPeople = []
    cursor = connection.cursor()

    cursor.execute("""
WITH
  winners AS
   (SELECT person_conducting_id, count(*) as winners
    FROM contests_contestresult r
    INNER JOIN contests_contestevent e ON e.id = r.contest_event_id
    INNER JOIN contests_contest c ON c.id = e.contest_id
    WHERE r.results_position = 1
    AND (c.group_id is null or c.group_id NOT IN (509,76,77)) -- whit friday Rochdale/Tameside/Saddleworth
    AND person_conducting_id != 310730
    GROUP BY person_conducting_id),
  total AS
   (SELECT person_conducting_id, count(*) as contests
    FROM contests_contestresult r
    INNER JOIN contests_contestevent e ON e.id = r.contest_event_id
    INNER JOIN contests_contest c ON c.id = e.contest_id
    AND (c.group_id is null or c.group_id NOT IN (509,76,77)) -- whit friday Rochdale/Tameside/Saddleworth
    AND person_conducting_id != 310730
    AND r.results_position < 1000
    GROUP BY person_conducting_id)
SELECT p.slug, p.surname, p.first_names, p.bandname, w.winners, t.contests
FROM people_person p
INNER JOIN winners w ON p.id = w.person_conducting_id
INNER JOIN total t ON p.id = t.person_conducting_id
ORDER BY 5 desc""")
    rows = cursor.fetchall()
    for row in rows:
        lPerson = ResultObject()
        lPerson.slug = row[0]
        lPerson.surname = row[1]
        lPerson.first_names = row[2]
        lPerson.bandname = row[3]
        lPerson.wins = row[4]
        lPerson.contests = row[5]
        lPerson.percent_win = (lPerson.wins * 100) // lPerson.contests
        if lPerson.contests >= 10:
            lPeople.append(lPerson)
    cursor.close()
    return render_auth(request, 'people/winners.html', {
                                                       'People' : lPeople,
                                                       })
