# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from django.db import connection

from bbr.decorators import login_required_pro_user
from bbr.render import render_auth


class SectionCount(object):
    pass

@login_required_pro_user
def section_counts(request):
    """
    Show sections and the count of bands within them
    """
    lUkSql = """WITH sections AS
  (SELECT COALESCE(b.national_grading,'') section, r.name region_name, r.slug region_slug, count(*) count
  FROM bands_band b
  INNER JOIN regions_region r on r.id = b.region_id
  LEFT OUTER JOIN regions_region c on c.id = r.container_id
  WHERE c.name = 'United Kingdom'
  AND b.status IN (1,2,3)
  GROUP BY 3, 2, 1)
SELECT section, region_name, count,
  CASE section
      WHEN 'Championship' THEN 1
      WHEN 'First' THEN 10
      WHEN 'Second' THEN 20
      WHEN 'Third' THEN 30
      WHEN 'Fourth' THEN 40
      WHEN 'Youth' THEN 50
      ELSE 99
    END as section_order,
    region_slug
FROM sections
ORDER BY 2, 4"""

    lUkSectionCounts = []

    cursor = connection.cursor()
    cursor.execute(lUkSql)
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            lSectionCount = SectionCount()
            lSectionCount.sectionName = row[0]
            lSectionCount.regionName = row[1]
            lSectionCount.count = row[2]
            lSectionCount.regionSlug = row[4]
            
            lUkSectionCounts.append(lSectionCount)
    cursor.close()
    
    
    lWorldSql = """WITH sections AS
  (SELECT COALESCE(b.national_grading,'') section, r.name region_name, r.slug region_slug, count(*) count
  FROM bands_band b
  INNER JOIN regions_region r on r.id = b.region_id
  AND b.status IN (1,2,3)
  AND r.container_id is null
  GROUP BY 3, 2, 1)
SELECT section, region_name, count,
  CASE section
      WHEN 'Championship' THEN 1
      WHEN 'Elite' THEN 1
      WHEN 'Excellence' THEN 2
      WHEN 'First' THEN 10
      WHEN 'A Grade' THEN 10
      WHEN 'Second' THEN 20
      WHEN 'B Grade' THEN 20
      WHEN 'Third' THEN 30
      WHEN 'C Grade' THEN 40
      WHEN 'Fourth' THEN 40
      WHEN 'D Grade' THEN 40
      WHEN 'Fifth' THEN 50
      WHEN 'Youth' THEN 60
      ELSE 99
    END as section_order,
    region_slug
FROM sections
ORDER BY 2, 4"""

    lWorldSectionCounts = []

    cursor = connection.cursor()
    cursor.execute(lWorldSql)
    rows = cursor.fetchall()
    if rows:
        for row in rows:
            lSectionCount = SectionCount()
            lSectionCount.sectionName = row[0]
            lSectionCount.regionName = row[1]
            lSectionCount.count = row[2]
            lSectionCount.regionSlug = row[4]
            
            lWorldSectionCounts.append(lSectionCount)
    cursor.close()
    
    
    return render_auth(request, 'sections/sections.html', {'UkSectionCounts' : lUkSectionCounts,
                                                           'WorldSectionCounts' : lWorldSectionCounts,
                                                           })