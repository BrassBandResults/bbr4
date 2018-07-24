# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from datetime import datetime, timedelta

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.http import Http404, HttpResponseRedirect

from bbr3.decorators import login_required_pro_user
from bbr3.siteutils import slugify, browser_details
from bbr3.render import render_auth
from contests.models import ContestEvent, ContestResult, ResultPiecePerformance
from people.models import Person
from pieces.forms import EditPieceForm
from pieces.models import  TestPiece, TestPieceAlias, DownloadTrack
from pieces.tasks import notification
from sections.models import Section
from users.models import PersonalContestHistory


def _fetch_piece_counts(pSectionId=None):
    """
    Return two dictionaries, one for own choice pieces (id->count) and the other for set tests, limited to contests in the specified section if specified
    """
    
    # find own choice piece performances
    own_choice_cursor = connection.cursor()
    lOwnChoiceResults = {}
    if pSectionId == None:
        lOwnChoiceSql = "SELECT test_piece_id, count(*) FROM contests_contestresult WHERE test_piece_id is not null GROUP BY test_piece_id"
        own_choice_cursor.execute(lOwnChoiceSql)
    else:
        lOwnChoiceSql = "SELECT test_piece_id, count(*) FROM contests_contestresult WHERE test_piece_id is not null AND contest_event_id IN (SELECT id FROM contests_contestevent WHERE contest_id IN (SELECT c.id FROM contests_contest c WHERE c.section_id =  %(section)s)) GROUP BY test_piece_id"
        own_choice_cursor.execute(lOwnChoiceSql, {'section' : pSectionId})
    simple_rows = own_choice_cursor.fetchall()
    for row in simple_rows:
        lOwnChoiceResults[row[0]] = row[1]
    own_choice_cursor.close()
    
    # find set test piece performances
    simple_cursor = connection.cursor()
    extra_cursor = connection.cursor()
    lSetTestResults = {}
    if pSectionId == None:
        lSetTestSql = "SELECT test_piece_id, count(*) from contests_contestevent where test_piece_id is not null group by test_piece_id"
        simple_cursor.execute(lSetTestSql)
        lExtraSetTest = "SELECT test_piece_id, count(*) FROM contests_contesttestpiece GROUP BY test_piece_id"
        extra_cursor.execute(lExtraSetTest)
    else:
        lSetTestSql = "SELECT test_piece_id, count(*) FROM contests_contestevent WHERE test_piece_id is not null AND contest_id in (SELECT c.id FROM contests_contest c WHERE c.section_id =  %(section)s) GROUP BY test_piece_id"
        simple_cursor.execute(lSetTestSql, {'section' : pSectionId})
        lExtraSetTest = "SELECT test_piece_id, count(*) FROM contests_contesttestpiece WHERE contest_event_id in (SELECT e.id FROM contests_contestevent e, contests_contest c WHERE e.contest_id = c.id AND c.section_id =  %(section)s) GROUP BY test_piece_id"
        extra_cursor.execute(lExtraSetTest, {'section' : pSectionId})
    own_choice_rows = simple_cursor.fetchall()
    for row in own_choice_rows:
        lSetTestResults[row[0]] = row[1]
    extra_rows = extra_cursor.fetchall()
    for row in extra_rows:
        try:
            lExistingCount = lSetTestResults[row[0]]
        except KeyError:
            lExistingCount = 0
        lSetTestResults[row[0]] = lExistingCount + row[1] 
    simple_cursor.close()
    extra_cursor.close()
    
    # find entertainments piece performances
    entertainments_cursor = connection.cursor()
    if pSectionId == None:
        lSetTestSql = "SELECT piece_id, count(*) FROM contests_resultpieceperformance WHERE piece_id is not null group by piece_id"
        entertainments_cursor.execute(lSetTestSql)
    else:
        lSetTestSql = """SELECT piece_id, count(*) 
                        FROM contests_resultpieceperformance p
                        INNER JOIN contests_contestresult r ON (p.result_id = r.id)
                        WHERE r.contest_event_id in (SELECT e.id FROM contests_contestevent e, contests_contest c WHERE e.contest_id = c.id AND c.section_id =  %(section)s) 
                        GROUP BY piece_id"""
        entertainments_cursor.execute(lSetTestSql, {'section' : pSectionId})
    ents_rows = entertainments_cursor.fetchall()
    for row in ents_rows:
        try:
            lExistingCount = lOwnChoiceResults[row[0]]
        except KeyError:
            lExistingCount = 0
        lOwnChoiceResults[row[0]] = lExistingCount + row[1] 
    entertainments_cursor.close()
    
    return lSetTestResults, lOwnChoiceResults

def piece_list(request):
    """
    Show list of pieces starting with A
    """
    return piece_list_filter_letter(request, 'A')
    
def piece_list_filter_letter(request, pLetter):
    """
    Show list of pieces that start with specified letter
    """
    lSetTestResults, lOwnChoiceResults = _fetch_piece_counts()
    
    lPieceQuery = TestPiece.objects.all().select_related('composer', 'arranger')
    lAliasQuery = TestPieceAlias.objects.all().select_related()
    if pLetter == 'ALL':
        lPieces = lPieceQuery
        lAliases = lAliasQuery
    elif pLetter == '0':
        lPieces = lPieceQuery.extra(where=["substr(pieces_testpiece.name, 1, 1) in ('0','1','2','3','4','5','6','7','8','9')"])
        lAliases = lAliasQuery.extra(where=["substr(pieces_testpiecealias.name, 1, 1) in ('0','1','2','3','4','5','6','7','8','9')"])
        pLetter = "0-9"
    else:
        lPieces = lPieceQuery.filter(name__istartswith=pLetter)
        lAliases = lAliasQuery.filter(name__istartswith=pLetter)
    for piece in lPieces:
        try:
            piece.own_choice_count = lOwnChoiceResults[piece.id]
        except KeyError:
            piece.own_choice_count = 0
           
        try:    
            piece.set_test_count = lSetTestResults[piece.id]
        except KeyError:
            piece.set_test_count = 0
    for alias in lAliases:
        try:
            alias.own_choice_count = lOwnChoiceResults[alias.piece_id]
        except KeyError:
            alias.own_choice_count = 0
           
        try:    
            alias.set_test_count = lSetTestResults[alias.piece_id]
        except KeyError:
            alias.set_test_count = 0
    lPieceCount = TestPiece.objects.all().count()
    return render_auth(request, 'pieces/pieces.html', {"Pieces" : lPieces,
                                                       "Aliases" : lAliases,
                                                       "ResultCount" : len(lPieces),
                                                       "PieceCount" : lPieceCount,
                                                       "StartsWith" : pLetter})
    
    
def single_piece(request, pPieceSlug):
    """
    Show a single test piece
    """
    try:
        lPiece = TestPiece.objects.filter(slug=pPieceSlug).select_related('composer', 'arranger')[0]
    except IndexError:
        raise Http404()
    
    # find list of contest event ids where this piece was an extra set test
    lContestEventIdsWhereSetTest = []
    lContestEventIdsWhereSetTestAnd = []
    lSetTestExtraSql = "SELECT contest_event_id, and_or FROM contests_contesttestpiece WHERE test_piece_id = %(piece_id)s"
    cursor = connection.cursor()
    cursor.execute(lSetTestExtraSql, {'piece_id' : lPiece.id})
    rows = cursor.fetchall()
    for row in rows:
        lContestEventIdsWhereSetTest.append(row[0])
        if row[1] == 'and':
            lContestEventIdsWhereSetTestAnd.append(row[0])
    cursor.close()
    
    # find this user's playing of this piece from their contest history
    lUserResultsForThisPiece = []
    if request.user.is_anonymous() == False:
        lUserResultsForThisPieceWithDate = []
        lUserHistoryThisPiece = PersonalContestHistory.objects.filter(user=request.user, status='accepted', result__contest_event__test_piece=lPiece).select_related('result', 'result__band', 'result__contest_event', 'result__contest_event__contest')
        if len(lUserHistoryThisPiece):
            for lUserHistory in lUserHistoryThisPiece:
                lUserResultsForThisPieceWithDate.append((lUserHistory.result.contest_event.date_of_event, lUserHistory.result))
        lUserOwnChoiceThisPiece = PersonalContestHistory.objects.filter(user=request.user, status='accepted', result__test_piece=lPiece).select_related('result', 'result__band', 'result__contest_event', 'result__contest_event__contest')
        if len(lUserOwnChoiceThisPiece):
            for lUserOwnChoiceHistory in lUserOwnChoiceThisPiece:
                lUserResultsForThisPieceWithDate.append((lUserOwnChoiceHistory.result.contest_event.date_of_event, lUserOwnChoiceHistory.result))
        lUserResultsForThisPieceWithDate.sort()
        lUserResultsForThisPieceWithDate.reverse()
        
        for result in lUserResultsForThisPieceWithDate:
            lUserResultsForThisPiece.append(result[1])
            
        lContestHistorysWithAdditionalTestPiece = PersonalContestHistory.objects.filter(user=request.user, status='accepted', result__contest_event__id__in=lContestEventIdsWhereSetTestAnd)
        for result in lContestHistorysWithAdditionalTestPiece:
            lUserResultsForThisPiece.append(result.result)
    
    # find list of contest event ids where this piece used as set test
    lSetTestSql = "SELECT id FROM contests_contestevent WHERE test_piece_id = %(piece_id)s"
    cursor = connection.cursor()
    cursor.execute(lSetTestSql, {'piece_id' : lPiece.id})
    rows = cursor.fetchall()
    for row in rows:
        lContestEventIdsWhereSetTest.append(row[0])
    cursor.close()
    
    # find all the contest events objects given both sets of ids
    lUsageSetTest = ContestEvent.objects.filter(id__in=lContestEventIdsWhereSetTest).select_related('contest')
    
    if len(lContestEventIdsWhereSetTest) > 0:
        # work out who won these set test piece contests
        lIdsString = str(tuple(lContestEventIdsWhereSetTest))
        lIdsStringLessBrackets = lIdsString[1:-1].strip()
        if lIdsStringLessBrackets.endswith(','):
            lIdsStringLessBrackets = lIdsStringLessBrackets[:-1]
        lWinnersSetTestSql = """SELECT e.id, r.band_name, b.name, b.slug 
                                FROM contests_contestresult r, bands_band b, contests_contestevent e 
                                WHERE e.id IN (%s) 
                                AND b.id = r.band_id 
                                AND r.contest_event_id = e.id
                                AND r.results_position = 1""" % lIdsStringLessBrackets
        cursor = connection.cursor()
        cursor.execute(lWinnersSetTestSql)
        rows = cursor.fetchall()
        for row in rows:
            lEventId = row[0]
            lContestBandName = row[1]
            lCurrentBandName = row[2]
            lBandSlug = row[3]
            for event in lUsageSetTest:
                if event.id == lEventId:
                    event.band_name = lContestBandName
                    event.current_band_name = lCurrentBandName
                    event.band_slug = lBandSlug
        cursor.close()
    
    
    # find out results where this piece was used as an own choice test piece
    lUsageOwnChoice = ContestResult.objects.filter(test_piece=lPiece).select_related('band','contest_event', 'contest_event__contest')
    lShowEdit = False
    if request.user.is_anonymous() == False:
        lShowEdit = request.user.profile.superuser or (request.user.profile.enhanced_functionality and request.user.id == lPiece.owner.id)
        
    lUsageEntertainments = ResultPiecePerformance.objects.filter(piece=lPiece).select_related('result')
    lUsageOwnChoiceAndEnts = []
    for own_choice in lUsageOwnChoice:
        lUsageOwnChoiceAndEnts.append(own_choice)
    for ents in lUsageEntertainments:
        lUsageOwnChoiceAndEnts.append(ents.result)
        
    lDownloadTracks = DownloadTrack.objects.filter(test_piece=lPiece).select_related('album', 'album__store')
    lDownloadAlbums = {}
    for track in lDownloadTracks:
        lDownloadAlbums[track.album.id] = track.album
    lDownloadAlbums = lDownloadAlbums.values()
    
    # Set test data for chart
    lSetTestYearCount = {}
    for event in lUsageSetTest:
        try:
            lCount = lSetTestYearCount[event.date_of_event.year]
        except KeyError:
            lCount = 0
        lCount += 1
        lSetTestYearCount[event.date_of_event.year] = lCount
        
    lSetTestChartData = ""
    lYear = lSetTestYearCount.keys()
    sorted(lYear)
    for year in lYear:
        lYearCount = lSetTestYearCount[year]
        lSetTestChartData += "['%d', %d]," % (year, lYearCount) 
        
    # Own choice data for chart
    lOwnChoiceYearCount = {}
    for result in lUsageOwnChoiceAndEnts:
        try:
            lCount = lOwnChoiceYearCount[result.contest_event.date_of_event.year]
        except KeyError:
            lCount = 0
        lCount += 1
        lOwnChoiceYearCount[result.contest_event.date_of_event.year] = lCount
        
    lOwnChoiceChartData = ""
    lYear = lOwnChoiceYearCount.keys()
    sorted(lYear)
    for year in lYear:
        lYearCount = lOwnChoiceYearCount[year]
        lOwnChoiceChartData += "['%d', %d]," % (year, lYearCount) 
        
    return render_auth(request, 'pieces/piece.html', {"Piece" : lPiece,
                                                      "UsageSetTest" : lUsageSetTest,
                                                      "UsageOwnChoice" : lUsageOwnChoiceAndEnts,
                                                      "UsageOwnChoiceCount" : len(lUsageOwnChoiceAndEnts),
                                                      "ShowEdit" : lShowEdit,
                                                      "UserResultsForThisPiece" : lUserResultsForThisPiece,
                                                      "UserResultsForThisPieceCount" : len(lUserResultsForThisPiece),
                                                      "DownloadAlbums" : lDownloadAlbums,
                                                      "OwnChoiceChartData" : lOwnChoiceChartData,
                                                      "SetTestChartData" : lSetTestChartData,
                                                      })

@login_required
def pieces_by_section(request):
    """
    Show a list of pieces sorted by section they have been set for
    """
    lChampionshipPieces = _get_pieces_for_section("Championship")
    lFirstPieces = _get_pieces_for_section("First")
    lSecondPieces = _get_pieces_for_section("Second")
    lThirdPieces = _get_pieces_for_section("Third")
    lFourthPieces = _get_pieces_for_section("Fourth")
    return render_auth(request, 'pieces/by_section.html', {"ChampionshipPieces" : lChampionshipPieces,
                                                           "FirstPieces" : lFirstPieces,
                                                           "SecondPieces" : lSecondPieces,
                                                           "ThirdPieces" : lThirdPieces,
                                                           "FourthPieces" : lFourthPieces,
                                                           })


def _get_pieces_for_section(pSectionName):
    """
    Return the pieces for a given section
    """
    lToday = datetime.now()
    lThirtyYearsAgo = lToday - timedelta(days=(30 * 365))
    lPieces = {}
    try:
        lSection = Section.objects.filter(name=pSectionName)[0]
    except IndexError:
        raise Http404()
    lSetTestResults, lOwnChoiceResults = _fetch_piece_counts(lSection.id)
    lContestEvents = ContestEvent.objects.filter(date_of_event__gte=lThirtyYearsAgo, contest__section=lSection).extra(select={
                'piece_name':'SELECT name FROM pieces_testpiece WHERE id = contests_contestevent.test_piece_id',
                'piece_slug':'SELECT slug FROM pieces_testpiece WHERE id = contests_contestevent.test_piece_id',
                'piece_composer':'SELECT composer_id FROM pieces_testpiece WHERE id = contests_contestevent.test_piece_id',
                'piece_arranger':'SELECT arranger_id FROM pieces_testpiece WHERE id = contests_contestevent.test_piece_id',
                }).select_related()
    lComposerArranger = {}                
    for contest_event in lContestEvents:
        if contest_event.piece_name:
            lTestPiece = TestPiece()
            lTestPiece.id = contest_event.test_piece_id
            lTestPiece.name = contest_event.piece_name
            lTestPiece.slug = contest_event.piece_slug
            lTestPiece.composer_id = contest_event.piece_composer
            lTestPiece.arranger_id = contest_event.piece_arranger
            lComposerArranger[lTestPiece.composer_id] = lTestPiece.composer_id
            lComposerArranger[lTestPiece.arranger_id] = lTestPiece.arranger_id
            try:
                lTestPiece.own_choice_count = lOwnChoiceResults[lTestPiece.id]
            except KeyError:
                lTestPiece.own_choice_count = 0
           
            try:    
                lTestPiece.set_test_count = lSetTestResults[lTestPiece.id]
            except KeyError:
                lTestPiece.set_test_count = 0
            
            lPieces[contest_event.piece_name] = lTestPiece 
    
    lComposers = Person.objects.filter(id__in=lComposerArranger.keys())
    for lPiece in lPieces.values():
        for lComposer in lComposers:
            if lComposer.id == lPiece.composer_id:
                lPiece.composer = lComposer
            if lComposer.id == lPiece.arranger_id:
                lPiece.arranger = lComposer
                
    return lPieces.values()

@login_required  
def add_piece(request):
    """
    Add a new test piece
    """
    if request.user.profile.superuser == False:
        if request.user.profile.enhanced_functionality == False:
            raise Http404()
    if request.method == 'POST':
        form = EditPieceForm(request.POST)
        if form.is_valid():
            lNewPiece = form.save(commit=False)
            lNewPiece.slug = slugify(lNewPiece.name, instance=lNewPiece)
            lNewPiece.lastChangedBy = request.user
            lNewPiece.owner = request.user
            lNewPiece.save()
            notification.delay(None, lNewPiece, 'piece', 'new', request.user, browser_details(request))            
            return HttpResponseRedirect('/pieces/')
    else:
        form = EditPieceForm()

    return render_auth(request, 'pieces/new_piece.html', {'form': form})
    
    
@login_required  
def edit_piece(request, pPieceSlug):
    """
    Edit a test piece
    """
    try:
        lPiece = TestPiece.objects.filter(slug=pPieceSlug)[0]
    except IndexError:
        raise Http404()
    if request.user.profile.superuser == False:
        if request.user.id != lPiece.owner.id:
            raise Http404() 
        if request.user.profile.enhanced_functionality == False:
            raise Http404()
    if request.method == 'POST':
        form = EditPieceForm(request.POST, instance=lPiece)
        if form.is_valid():
            lOldPiece = TestPiece.objects.filter(id=lPiece.id)[0]
            lNewPiece = form.save(commit=False)
            lNewPiece.lastChangedBy = request.user
            lNewPiece.save()
            notification.delay(lOldPiece, lNewPiece, 'piece', 'edit', request.user, browser_details(request))
            return HttpResponseRedirect('/pieces/%s/' % lPiece.slug)
    else:
        form = EditPieceForm(instance=lPiece)

    return render_auth(request, 'pieces/edit_piece.html', {'form': form, "Piece" : lPiece})    

@login_required
def piece_options(request):
    """
    Return <option> tags for droplist of test pieces
    """
    try:
        lExclude = request.GET['exclude']
        lPieces = TestPiece.objects.exclude(id=lExclude)
    except KeyError:
        lPieces = TestPiece.objects.all()
    return render_auth(request, 'pieces/option_list.htm', {"Pieces" : lPieces})

class PieceRank(object):
    pass


@login_required_pro_user
def best_own_choice(request):
    """
    Rank most successful own choice pieces
    """
    lBestOwnChoice = {}
    lPieceNames = {}
    cursor = connection.cursor()
    lOwnChoiceSql = """
       SELECT r.results_position, p.slug, p.name 
       FROM contests_contestresult r
       INNER JOIN pieces_testpiece p ON r.test_piece_id = p.id  
       INNER JOIN contests_contestevent e ON e.id = r.contest_event_id
       INNER JOIN contests_contest c ON c.id = e.contest_id
       WHERE r.results_position < 4
       AND (c.group_id is NULL OR c.group_id NOT IN (509,76.77)) -- whit friday Rochdale/Tameside/Saddleworth"""
    cursor.execute(lOwnChoiceSql)
    rows = cursor.fetchall()
    for row in rows:
        lPosition = row[0]
        lPieceSlug = row[1]
        lPieceName = row[2]
        lPieceNames[lPieceSlug] = lPieceName
        try:
            lExistingData = lBestOwnChoice[lPieceSlug]
        except KeyError:
            lExistingData = (0, 0)
        lNewScore = lExistingData[0] + settings.OWN_CHOICE_POINTS[lPosition]
        lNewCount = lExistingData[1] + 1
        lBestOwnChoice[lPieceSlug] = (lNewScore, lNewCount)
    cursor.close()
    
    lPointsTuples = []
    for slug, points in lBestOwnChoice.items():
        lPointsTuples.append((points, slug, lPieceNames[slug]))
    lPointsTuples.sort()
    lPointsTuples.reverse()
    
    # lPointsTuples in now in order
    lPieces = []
    for row in lPointsTuples:
        lPiece = PieceRank()
        lPiece.count = row[0][1]
        lPiece.points = row[0][0]
        lPiece.slug = row[1]
        lPiece.name = row[2]
        lPieces.append(lPiece)
    
    return render_auth(request, 'pieces/best_own_choice.html', {'Pieces' : lPieces})

