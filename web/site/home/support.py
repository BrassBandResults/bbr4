# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved
from django.db import connection

class ThisWeek(object):
    pass

def _fetch_this_week_in_history():
    """
    Fetch winners of events that took place this week in history
    """
    lThisWeek = None
    cursor = connection.cursor()
    cursor.execute("""SELECT e.name, c.slug, e.date_of_event, r.band_name, b.slug, b.name 
                      FROM contests_contest c
                      INNER JOIN contests_contestevent e ON e.contest_id = c.id
                      INNER JOIN contests_contestresult r ON r.contest_event_id = e.id 
                      INNER JOIN bands_band b ON r.band_id = b.id
                      WHERE to_char(e.date_of_event, 'WW') = to_char(current_date, 'WW') 
                      AND to_char(e.date_of_event, 'DD') != '01' 
                      AND e.date_of_event < current_date - 400
                      AND r.results_position = 1 
                      ORDER BY random() 
                      LIMIT 1""")
    rows = cursor.fetchall()
    if rows and rows[0]:
        lThisWeek = ThisWeek()
        lThisWeek.contest_name = rows[0][0]
        lThisWeek.contest_slug = rows[0][1]
        lThisWeek.date_of_event = rows[0][2]
        lThisWeek.band_name = rows[0][3]
        lThisWeek.band_slug = rows[0][4]
        lThisWeek.current_band_name = rows[0][5]
    
    return lThisWeek