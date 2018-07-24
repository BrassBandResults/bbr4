# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved


from django.db import connection

def calculate_overall_winners(pContestGroup, pContestsRequired, pYear):
    """
    for each year
      for each band that competed at six contests in the group that year
        Add together the lowest six numbers in the results

    The band with the lowest number overall is the winner
    """
    # Work out how many bands competed that year
    lCursor = connection.cursor()
    lCursor.execute("SELECT count(distinct(r.band_id)) FROM contests_contestresult r, contests_contestevent e, contests_contest c WHERE r.contest_event_id = e.id AND e.contest_id = c.id AND c.group_id = %(groupid)s AND extract(year from e.date_of_event) = %(year)s", {'groupid': pContestGroup.id, 'year' : pYear})
    lRows = lCursor.fetchall()
    for row in lRows:
        lBandsCompeting = row[0]
    lCursor.close()

    # get full results for that year - first element is the winner
    lResults = calculate_overall_results(pContestGroup, pContestsRequired, pYear)
    try:
        lWinner = lResults[0]
    except IndexError:
        lWinner = {}
    return lWinner, lBandsCompeting
    

def calculate_overall_results(pContestGroup, pContestsRequired, pYear):
    """
    Work out the overall results for a Whit Friday contest
    """
    # Find out how many contests each band has done
    lCursor = connection.cursor()
    lCursor.execute("SELECT r.band_id, count(*) FROM contests_contestresult r, contests_contestevent e, contests_contest c WHERE r.contest_event_id = e.id AND e.contest_id = c.id AND c.group_id = %(groupid)s AND r.results_position < 9996 AND extract(year from e.date_of_event) = %(year)s AND c.exclude_from_group_results = false GROUP BY r.band_id", {'groupid': pContestGroup.id, 'year' : pYear})
    lRows = lCursor.fetchall()
    lResults = {}
    for row in lRows:
        lBandId = row[0]
        lResultCount = int(row[1])
        if lResultCount >= pContestsRequired:
            lResults[str(lBandId)] = lResultCount
    lCursor.close()
    
    lBandIds = ",".join(lResults.keys())
    
    if len(lBandIds) == 0:
        return []

    lCursor = connection.cursor()
    lCursor.execute("SELECT r.results_position, b.slug, r.band_name FROM bands_band b, contests_contestresult r, contests_contestevent e, contests_contest c WHERE b.id = r.band_id AND r.contest_event_id = e.id AND e.contest_id = c.id AND c.group_id = %s AND r.results_position < 9999 AND r.band_id IN (%s) AND extract(year from e.date_of_event) = %s AND c.exclude_from_group_results = false" % (pContestGroup.id, lBandIds, pYear))
    lRows = lCursor.fetchall()
    lBands = {}
    lBandResults = {}
    for row in lRows:
        lPosition = row[0]
        if int(lPosition) == 0 or int(lPosition) > 9900:
            continue
        lBandSlug = row[1]
        lBandName = row[2]
        
        lBands[lBandSlug] = lBandName
        try:
            lExistingResults = lBandResults[lBandSlug]
            lExistingResults.append(lPosition)
        except KeyError:
            lExistingResults = []
            lExistingResults.append(lPosition)
            lBandResults[lBandSlug] = lExistingResults
    
    # Get total points for each band
    lBandTotals = {}
    lBandTotalsWithTieBreak = {}
    lBandSeventhResult = {}
    lFirstSixBandResults = {}
    for band_slug in lBandResults.keys():
        lFirstSixBandResults[band_slug] = sorted(lBandResults[band_slug])[:pContestsRequired]
        try:
            lBandSeventhResult[band_slug] = sorted(lBandResults[band_slug])[pContestsRequired]
        except IndexError:
            # band didn't compete in a seventh contest, so the results is worse than if they did
            lBandSeventhResult[band_slug] = 9999 
        lTotalPoints = sum(lFirstSixBandResults[band_slug])
        lTotalPointsPlusTieBreak = lTotalPoints + (1 - (1.0 / lBandSeventhResult[band_slug]))
        lBandTotals[band_slug] = lTotalPoints
        lBandTotalsWithTieBreak[band_slug] = lTotalPointsPlusTieBreak 
        
    lDecoratedList = [(points, slug) for slug, points in lBandTotalsWithTieBreak.items()]
    lDecoratedList.sort()
    lSortedResults = [{'slug':slug, 'points':points} for points, slug in lDecoratedList]
    lPosition = 1
    for row in lSortedResults:
        row['band'] = lBands[row['slug']] 
        row['position'] = lPosition
        row['display_points'] = lBandTotals[row['slug']]
        row['tiebreak'] = lBandSeventhResult[row['slug']]
        lPosition += 1

    return lSortedResults