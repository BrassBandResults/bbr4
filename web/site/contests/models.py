# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved



from datetime import datetime, date, timedelta
import json

from django.contrib.auth.models import User
from django.contrib.gis.db import models as geomodels
from django.contrib.gis.geos.factory import fromstr
from django.core.exceptions import ObjectDoesNotExist
from django.db import connection, models
from django.utils.dateformat import format

from bands.models import Band
from contests.whitfriday import calculate_overall_winners, \
    calculate_overall_results
from people.models import Person
from pieces.models import TestPiece
from regions.models import Region
from sections.models import Section
from tags.models import ContestTag


class Venue(models.Model):
    """
    A venue for a contest
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    country = models.ForeignKey(Region, on_delete=models.PROTECT, blank=True, null=True)
    latitude = models.CharField(max_length=15, blank=True, null=True)
    longitude = models.CharField(max_length=15, blank=True, null=True)
    point = geomodels.PointField(dim=3, geography=True, blank=True, null=True, editable=False)
    postcode = models.CharField(max_length=10, blank=True, null=True)
    exact = models.BooleanField(default=False, help_text="True if latitude and longitude is for a building, rather than a town")
    mapper = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='VenueMapper', blank=True, null=True)
    parent = models.ForeignKey("self", on_delete=models.PROTECT, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    lastChangedBy = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='VenueLastChangedBy')
    owner = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='VenueOwner')
        
    def __str__(self):
        return "%s" % (self.name)
    
    def asJson(self):
        lDict = {
                 'id' : self.id,
                 'name' : self.name,
                 }
        return json.dumps(lDict)
    
    def venue_name(self, pDateOfEvent):
        """
        Return venue name, or alias name if there is an alias for the date specified
        """
        try:
            lAliasMatch = VenueAlias.objects.filter(venue=self, alias_start_date__lte=pDateOfEvent, alias_end_date__gte=pDateOfEvent)[0]
            return lAliasMatch.name
        except IndexError:
            return self.name
    
    def save(self):
        if self.latitude != None and len(self.latitude) > 0 and self.longitude != None and len(self.longitude) > 0:
            lString = 'POINT(%s %s)' % (self.longitude.strip(), self.latitude.strip())
            self.point = fromstr(lString)
        self.last_modified = datetime.now()
        super(Venue, self).save()
    
    class Meta:
        ordering = ['name'] 
        

class VenueAlias(models.Model):
    """
    An alias for a venue
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    name = models.CharField(max_length=200, help_text='Name of Venue Alias')
    alias_start_date = models.DateField(blank=True, null=True, help_text="Start date for this alias (yyyy-mm-dd)")
    alias_end_date = models.DateField(blank=True, null=True, help_text="End date for this alias (yyyy-mm-dd)")
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)
    lastChangedBy = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='VenueAliasLastChangedBy')
    owner = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='VenueAliasOwner')
    
    def save(self):
        self.last_modified = datetime.now()
        super(VenueAlias, self).save()
        
    def show_start_date(self):
        """
        Return true if start date is recent enough to make sense
        """
        lCutOffDate = date(year=1700, month=1, day=1)
        if self.alias_start_date > lCutOffDate:
            return True
        return False
     
    @property
    def slug(self):
        return self.venue.slug
    
    def __str__(self):
        return "%s -> %s" % (self.name, self.venue.name)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Venue aliases'
        db_table = 'venues_venuealias'
        

class ContestGroup(models.Model):
    """
    A container for a contest, for example an Area contest that contains all of the sections
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    name = models.CharField(max_length=100, help_text='Name of Contest Group')
    slug = models.SlugField()
    TYPE_CHOICES = (
                    ('S', 'Simple'),
                    ('W', 'Whit Friday'),
                    )
    group_type = models.CharField(max_length=1, default='S', choices=TYPE_CHOICES)
    notes = models.TextField(blank=True, null=True)
    tags = models.ManyToManyField(ContestTag, blank=True)
    lastChangedBy = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='ContestGroupLastChangedBy')
    owner = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='ContestGroupOwner')
    
    def save(self):
        self.last_modified = datetime.now()
        super(ContestGroup, self).save()
        
    @property
    def count(self):
        lCount = 0
        for contest in self.contest_set.all():
            lCount += contest.count
        return lCount
    
    def tag_list(self):
        return self.tags.order_by('name').all()
    
    @property
    def actual_slug(self):
        return self.slug.upper()
    
    @property
    def links(self):
        return self.contestgroupweblink_set.order_by('order')
    
    def winners(self):
        """
        Return array of overall winners over the years, if this is a whit friday contest.  Bands must have competed at more 
        than six contests in this group to qualify
        """
        lCursor = connection.cursor()
        lCursor.execute("SELECT distinct e.date_of_event, e.date_resolution FROM contests_contestevent e, contests_contest c WHERE e.contest_id = c.id AND c.group_id = %(groupid)s order by e.date_of_event desc", {'groupid': self.id})
        lRows = lCursor.fetchall()
        lDates = []
        for row in lRows:
            lDates.append((row[0], row[1]))
        lCursor.close()
        lWinners = []
        for contest_date in lDates:
            lEventDate = contest_date[0]
            lDateResolution = contest_date[1]
            if lDateResolution == 'D':
                lDisplayDate = format(lEventDate, "jS M Y")
            elif lDateResolution == 'M':
                lDisplayDate = format(lEventDate, "M Y")
            elif lDateResolution == 'Y':
                lDisplayDate = format(lEventDate, "Y")
            lWinner, lBandsCompeting = calculate_overall_winners(self, pContestsRequired=6, pYear=lEventDate.year)
            lWinners.append({'date' : lEventDate, 'date_resolution' : lDateResolution, 'event_date' : lDisplayDate, 'winner' : lWinner, 'bands_competing' : lBandsCompeting})
        return lWinners
    
    def group_results(self, pYear):
        """
        Return the results for a particular year
        """
        lResults = calculate_overall_results(self, pContestsRequired=6, pYear=pYear)
        return lResults
    
    def get_absolute_url(self):
        """
        Used on the calendar, where we've set a date_of_event so we can return a reference
        to a particular year of a contest group
        """
        try:
            lDate = self.date_of_event
            return "/contests/%s/%d/" % (self.slug.upper(), lDate.year)
        except AttributeError:
            return "/contests/%s/" % (self.slug.upper())
    
    def __str__(self):
        return "%s" % self.name
    
    class Meta:
        ordering = ['name']
        

class ContestGroupAlias(models.Model):
    """
    An alias for a contest group
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    name = models.CharField(max_length=100, help_text='Name of Contest Group')
    group = models.ForeignKey(ContestGroup, on_delete=models.CASCADE)
    lastChangedBy = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='ContestGroupAliasLastChangedBy')
    owner = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='ContestGroupAliasOwner')
    
    def save(self):
        self.last_modified = datetime.now()
        super(ContestGroupAlias, self).save()
     
    @property    
    def count(self):
        return self.group.count
        
    @property
    def actual_slug(self):
        return self.group.actual_slug
    
    @property
    def slug(self):
        return self.group.slug
    
    def __str__(self):
        return "%s -> %s" % (self.name, self.group.name)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Contest Group aliases'
        
        
class ContestType(models.Model):
    """
    Type of contest.  If text fields are populated, that entity is required for this contest type.  So if second draw has a description, there are two
    draws at the contest.
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    name = models.CharField(max_length=100)
    first_draw = models.CharField(max_length=20, default="Draw", help_text="Title for first draw field")
    second_draw = models.CharField(max_length=20, blank=True, help_text="Title for second draw field")
    total_points = models.CharField(max_length=20, default="Points", help_text="Title for total points field")
    points_one = models.CharField(max_length=20, blank=True, help_text="Title for first split points field")
    points_two = models.CharField(max_length=20, blank=True, help_text="Title for first split points field")
    points_three = models.CharField(max_length=20, blank=True, help_text="Title for first split points field")
    points_four = models.CharField(max_length=20, blank=True, help_text="Title for first split points field")
    penalty_points = models.CharField(max_length=20, blank=True, help_text="Title for penalty points field")
    test_piece = models.BooleanField(default=True, blank=True, help_text="Contest has set test piece")
    own_choice = models.BooleanField(default=False, blank=True, help_text="Contest has own choice test piece")
    entertainments = models.BooleanField(default=False, blank=True, help_text="Contest has entertainments part")
    statistics = models.BooleanField(default=False, help_text="Show Adjudicator A/B/C Statistics")
    statistics_limit = models.IntegerField(default=2, help_text="Number of points fields to use for stats")
    lastChangedBy = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='ContestTypeLastChangedBy')
    owner = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='ContestTypeOwner')
    
    def save(self):
        self.last_modified = datetime.now()
        super(ContestType, self).save()
        
    def __str__(self):
        return "%s" % (self.name)
    
    class Meta:
        ordering = ['name']
    

class Contest(models.Model):
    """
    A contest in the brass band calendar, one record for Masters, Open, Yorkshire Area etc.
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    name = models.CharField(max_length=100, help_text='Name of Contest')
    group = models.ForeignKey(ContestGroup, blank=True, null=True, on_delete=models.PROTECT)
    slug = models.SlugField()
    description = models.TextField(blank=True)
    region = models.ForeignKey(Region, on_delete=models.PROTECT, blank=True, null=True, help_text='Region bands are drawn from.  Leave blank for non-region limited contests.')
    section = models.ForeignKey(Section, on_delete=models.PROTECT, blank=True, null=True, help_text='Section for contest.  Leave blank if not applicable or contest is not nationally graded')
    ordering = models.IntegerField(default=0, help_text='Order to show contest in group.  Higher numbers are later in the list')
    contest_type_link = models.ForeignKey(ContestType, on_delete=models.PROTECT, default=12, help_text="This controls the draw and points fields shown when adding/editing an event for this contest")
    qualifies_for = models.ForeignKey('Contest', on_delete=models.PROTECT, blank=True, null=True, help_text='Finals for this contest')
    hashtag = models.CharField(max_length=25, blank=True, null=True)
    contact_info = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    extinct = models.BooleanField(default=False, help_text="This marks the contest as one that is no longer run")
    exclude_from_group_results = models.BooleanField(default=False, help_text='If true, this contest is not included in total points calculated from the group (ie Overall Whit Friday)')
    all_events_added = models.BooleanField(default=False, help_text="This hides the prompt to add more results if contest extinct")
    period = models.IntegerField(blank=True, null=True, help_text="Number of years this contest repeats over.  If this is non null, allows contests between 14 months and 60 months to be included in current champions")
    prevent_future_bands = models.BooleanField(default=False, help_text="If true, prevents bands being added to the contest event whilst it is still in the future")
    tags = models.ManyToManyField(ContestTag, blank=True)
    lastChangedBy = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='ContestLastChangedBy')
    owner = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='ContestOwner')
    
    def __str__(self):
        return "%s" % (self.name)
    
    def get_absolute_url(self):
        return "/contests/%s/" % self.slug
    
    def tag_list(self):
        lUniqueTags = {}
        for tag in self.tags.all():
            lUniqueTags[tag.slug] = tag
        if self.group:
            for tag in self.group.tag_list():
                lUniqueTags[tag.slug] = tag
        lUniqueTagsKeys = sorted(lUniqueTags.keys())

        lReturn = []
        for lEachTagKey in lUniqueTagsKeys:
            lReturn.append(lUniqueTags[lEachTagKey])

        return lReturn
        
    
    def asJson(self):
        lRegionName = ""
        if self.region:
            lRegionName = self.region.name
        lDict = {
                 'id' : self.id,
                 'name' : self.name,
                 'contest_type' : self.contest_type_link.id,
                 'contest_type_display' : self.get_contest_type_link.name,
                 'region' : lRegionName,
                 }
        return json.dumps(lDict)
    
    def save(self):
        lMakeSlugUnique=False
        if not self.id and len(self.slug) == 50:
            # we have a full length slug - possibly not unique
            lMakeSlugUnique=True
                
        self.last_modified = datetime.now()
        super(Contest, self).save()
        
        if lMakeSlugUnique:
            self.slug = self.slug[0:40] + '-' + str(self.id)
            super(Contest, self).save()
        
    @property
    def links(self):
        lWebLinks = []
        for link in self.contestweblink_set.order_by('order'):
            lWebLinks.append(link)
        if self.group:
            for grouplink in self.group.links:
                lWebLinks.append(grouplink)
        return lWebLinks
        
    
    @property
    def count(self):
        return self.contestevent_set.count()
    
    @property
    def actual_slug(self):
        return self.slug
    
    def name_name_only(self):
        """
        Return just the contest name, without any section in brackets
        """
        lBracketIndex = self.name.rfind('(')
        if lBracketIndex > 0:
            return self.name[:lBracketIndex].strip()
        else:
            return self.name
        
    def name_section_only(self):
        """
        Return just the brackets part of the contest name, or empty string
        """
        lBracketIndex = self.name.rfind('(')
        if lBracketIndex > 0:
            return self.name[lBracketIndex:].strip()
        else:
            return ""
    
    class Meta:
        ordering = ['name']
        

class ContestAlias(models.Model):
    """
    An alias for a contest 
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    name = models.CharField(max_length=100, help_text='Name of Contest')
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    lastChangedBy = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='ContestAliasLastChangedBy')
    owner = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='ContestAliasOwner')
    
    def save(self):
        self.last_modified = datetime.now()
        super(ContestAlias, self).save()
     
    @property
    def actual_slug(self):
        return self.contest.actual_slug
     
    @property
    def slug(self):
        return self.contest.slug
    
    @property
    def count(self):
        return self.contest.count
    
    def __str__(self):
        return "%s -> %s" % (self.name, self.contest.name)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Contest aliases'


class ContestEvent(models.Model):
    """
    A contest event, a particular running of the Masters, Open, Yorkshire Area
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    date_of_event = models.DateField()
    DATE_RESOLUTION_CHOICES = (
        ('D', 'Exact Date'),
        ('M', 'Month and Year'),
        ('Y', 'Year'),
    )
    date_resolution = models.CharField(max_length=1, default='D', choices=DATE_RESOLUTION_CHOICES)
    contest = models.ForeignKey(Contest, on_delete=models.PROTECT)
    name = models.CharField(max_length=100)
    test_piece = models.ForeignKey(TestPiece, blank=True, null=True, on_delete=models.PROTECT)
    notes = models.TextField(blank=True)
    venue_link = models.ForeignKey(Venue, blank=True, null=True, on_delete=models.PROTECT)
    complete = models.BooleanField(default=False, help_text='Complete means stop prompting with "add more results"')
    no_contest = models.BooleanField(default=False, help_text='Set to true if no contest took place this year')
    contest_type_override_link = models.ForeignKey(ContestType, on_delete=models.PROTECT, blank=True, null=True)
    requires_input = models.BooleanField(default=False, help_text="There is data to input from scanned programme pages")
    lastChangedBy = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='ContestEventLastChangedBy')
    owner = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='ContestEventOwner')
    original_owner = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, blank=True, null=True, related_name='ContestEventOriginalOwner')
        
    def __str__(self):
        return "%s: %s" % (self.date_of_event, self.name)
    
    def future(self):
        lToday = date.today()
        return self.date_of_event > lToday
    
    def moreThanThreeMonthsInFuture(self):
        lToday = date.today()
        lThreeMonths = lToday + timedelta(days=90)
        return self.date_of_event > lThreeMonths
    
    @property
    def hashtag(self):
        return self.contest.hashtag
    
    @property
    def name_migrate(self):
        return self.name.replace("'", "''")
    
    @property
    def notes_migrate(self):
        if self.notes == None:
            return ''
        return self.notes.replace("'", "''").replace(";", ",")
    
    def tag_list(self):
        return self.contest.tag_list()
    
    @property
    def contest_type_link(self):
        if self.contest_type_override_link == None:
            return self.contest.contest_type_link
        return self.contest_type_override_link
    
    @property
    def contest_type(self):
        if self.contest_type_override_link == None:
            return self.contest.contest_type_link
        return self.contest_type_override_link
    
    
    @property
    def event_date_with_day(self):
        lFunctions = {
         'D': format(self.date_of_event, "D jS M Y"),
         'M': format(self.date_of_event, "M Y"),
         'Y': format(self.date_of_event, "Y"),
         }
        return lFunctions[self.date_resolution] 
    
    @property
    def event_date_link(self):
        lFunctions = {
         'D': '%d/%d/%d/' % (self.date_of_event.year, self.date_of_event.month, self.date_of_event.day),
         'M': '%d/%d/' % (self.date_of_event.year, self.date_of_event.month),
         'Y': '%d/' % (self.date_of_event.year),
         }
        return lFunctions[self.date_resolution] 
    
    @property
    def event_date(self):
        lFunctions = {
         'D': format(self.date_of_event, "jS M Y"),
         'M': format(self.date_of_event, "M Y"),
         'Y': format(self.date_of_event, "Y"),
         }
        return lFunctions[self.date_resolution] 
    
    @property
    def event_year(self):
        return format(self.date_of_event, "Y")
    
    @property
    def previous(self):
        """
        Return the previous entry for this contest in the database
        """
        try:
            return self.get_previous_by_date_of_event(contest=self.contest)
        except ObjectDoesNotExist:
            return None
        
    @property
    def next(self):
        """
        Return the next entry for this contest in the database
        """
        try:
            return self.get_next_by_date_of_event(contest=self.contest)
        except ObjectDoesNotExist:
            return None
        
    def not_complete(self):
        """
        Return True if this event is likely to have more results, and False if it looks complete
        """
        if self.complete:
            return False
        
        lResultCount = 0
        lMaxDraw = 0
        lMaxPosition = 0
        for result in self.contestresult_set.all():
            lResultCount += 1
            if result.draw > lMaxDraw:
                lMaxDraw = result.draw
            if result.results_position > lMaxPosition:
                lMaxPosition = result.results_position
        if lMaxDraw > lResultCount:
            return True
        if lMaxPosition > lResultCount:
            return True
        if lResultCount == 0:
            return True
        if lResultCount == 1:
            return True
        return False
    
    @property
    def competing_bands(self):
        try:
            lCompetingBands = self._competingBands
        except AttributeError:
            lCompetingBands = self.contestresult_set.count()
            self._competingBands = lCompetingBands
        return lCompetingBands
    
    def winners(self):
        return self.contestresult_set.select_related('band','band__region').filter(results_position=1)
    
    def get_absolute_url(self):
        return "/contests/%s/%s/" % (self.contest.slug, self.date_of_event)
    
    def adjudicators(self):
        lAdjudicators = {}
        for lContestAdjudicator in self.contestadjudicator_set.all():
            lKey = "%s%s" % (lContestAdjudicator.adjudicator.surname, lContestAdjudicator.adjudicator.id) 
            lAdjudicators[lKey] = lContestAdjudicator.adjudicator
            
        lSurnames = lAdjudicators.keys()
        lSurnames.sort()
        return [lAdjudicators[key] for key in lSurnames]
    
    def venue_name(self):
        """
        Show name of venue
        """
        if self.venue_link:
            return self.venue_link.venue_name(self.date_of_event)
        return "";
    
    def save(self):
        self.last_modified = datetime.now()
        if not self.original_owner:
            self.original_owner = self.owner
        super(ContestEvent, self).save()
    
    class Meta:
        ordering = ['-date_of_event', 'contest__group']
        
        
class ContestGroupLinkEventLink(models.Model):
    """
    Allows a contest event to be part of a second contest group
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    contest = models.ForeignKey(Contest, on_delete=models.PROTECT)
    event = models.ForeignKey(ContestEvent, on_delete=models.PROTECT)
    
    def __str__(self):
        return "%s -> %s" % (self.event.name, self.contest.name)
    
    def save(self):
        self.last_modified = datetime.now()
        super(ContestGroupLinkEventLink, self).save()
    
    
LOWEST_SPECIAL_POSITION = 9998 # change this if you add any more - greater than this number is "special"

UNPLACED_RESULTS_POSITION = 9999
DISQUALIFIED_RESULTS_POSITION = 10000
WITHDRAWN_RESULTS_POSITION = 10001       
        
class ContestResult(models.Model):
    """
    A contest result for a given band at a given event
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    contest_event = models.ForeignKey(ContestEvent, on_delete=models.PROTECT)
    band = models.ForeignKey(Band, on_delete=models.PROTECT)
    results_position = models.IntegerField(help_text="Position at contest, or 9999 for Unknown, 10000 for Disqualified, 10001 for Withdrawn")
    band_name = models.CharField(max_length=100)
    draw = models.IntegerField(default=0, help_text="Draw for order of play")
    draw_second_part = models.IntegerField(blank=True, null=True, help_text="Draw for the second part of the contest, if any")
    points = models.CharField(max_length=100, blank=True, null=True, help_text="Total points the band were awarded for this contest")
    points_first_part = models.CharField(max_length=10, blank=True, null=True, help_text="Points for first part, ie playing mark or test piece section")
    points_second_part = models.CharField(max_length=10, blank=True, null=True, help_text="Points for second part, ie entertainment mark or entertainments section")
    points_third_part = models.CharField(max_length=10, blank=True, null=True, help_text="Points for third part")
    points_fourth_part = models.CharField(max_length=10, blank=True, null=True, help_text="Points for fourth part")
    penalty_points = models.CharField(max_length=10, blank=True, null=True, help_text="Penalty points to take off the band")
    person_conducting = models.ForeignKey(Person, on_delete=models.PROTECT, blank=True, null=True)
    second_person_conducting = models.ForeignKey(Person, on_delete=models.PROTECT, related_name='SecondPersonConductor', default=None, blank=True, null=True)
    conductor_name = models.CharField(max_length=100, blank=True, null=True, help_text="Originally entered conductor name")
    notes = models.TextField(blank=True)
    test_piece = models.ForeignKey(TestPiece, blank=True, null=True, help_text="(Own choice contest only)", on_delete=models.PROTECT)
    lastChangedBy = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='ContestResultLastChangedBy')
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name='ContestResultOwner')
    original_owner = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, blank=True, null=True, related_name='ContestResultOriginalOwner')
    
        
    def __str__(self):
        return "%s: %s, %s" % (self.contest_event.name, self.band_name, self.results_position)
    
    def save(self):
        if self.results_position == 0 or self.results_position == '0' or self.results_position == None:
            self.results_position = UNPLACED_RESULTS_POSITION
        elif self.results_position == "W":
            self.results_position = WITHDRAWN_RESULTS_POSITION
        elif self.results_position == "D":
            self.results_position = DISQUALIFIED_RESULTS_POSITION
            
        if self.draw == 'W':
            self.draw = 0
            self.results_position = WITHDRAWN_RESULTS_POSITION
            
        self.last_modified = datetime.now()
        if not self.original_owner:
            self.original_owner = self.owner
        super(ContestResult, self).save()
        
    def delete(self):
        try:
            lProfile = self.owner.profile
            lProfile.remove_points_and_save(self.id, 'ContestResult')
        except IndexError:
            pass
        super(ContestResult, self).delete()
        
    @property
    def points_display(self):
        """
        Show draw for display on page
        """
        lReturn = ""
        if self.points:
            if self.points != '0':
                lReturn = self.points
        return lReturn
    
    @property
    def results_position_display(self):
        """
        Show position for display on page
        """
        lReturn = ""
        if self.results_position:
            if self.results_position == UNPLACED_RESULTS_POSITION:
                lReturn = ""
            elif self.results_position == DISQUALIFIED_RESULTS_POSITION:
                lReturn = "D"
            elif self.results_position == WITHDRAWN_RESULTS_POSITION:
                lReturn = "W"
            else:    
                lReturn = self.results_position
        else:
            if self.contest_event.no_contest:
                lReturn = "C"             
        return lReturn
    
    @property
    def results_position_display_long(self):
        """
        Show position for display on page
        """
        lReturn = ""
        if self.contest_event.no_contest:
            return "Cancelled"
        if self.results_position:
            if self.results_position == UNPLACED_RESULTS_POSITION:
                lReturn = "Unknown Result"
            elif self.results_position == DISQUALIFIED_RESULTS_POSITION:
                lReturn = "Disqualified"
            elif self.results_position == WITHDRAWN_RESULTS_POSITION:
                lReturn = "Withdrawn"
            else:    
                lReturn = self.results_position
        return lReturn
    
    
    @property
    def has_conductor(self):
        lUnknown = Person.objects.filter(slug='unknown')[0]
        if self.person_conducting_id == None or self.person_conducting_id == 0 or self.person_conducting_id == lUnknown.id:  
            return False
        return True
    
    @property
    def has_test_piece(self):
        return self.test_piece_id != None
    
    def piece_played(self):
        if self.test_piece:
            return self.test_piece
        if self.contest_event.test_piece:
            return self.contest_event.test_piece
        return None
    
    @property
    def band_name_export(self):
        if self.band_name == None:
            return ''
        return self.band_name.replace("'", "''")
    
    @property
    def notes_migrate(self):
        if self.notes == None:
            return ''
        return self.notes.replace("'", "''").replace(";", ",")
    
    class Meta:
        ordering = ['-contest_event__date_of_event','results_position','draw','band__name']
        
        
class ContestWeblink(models.Model):
    """
    A link to a website for a contest
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    contest = models.ForeignKey(Contest, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    website = models.CharField(max_length=255)
    order = models.IntegerField(default=10)
    lastChangedBy = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='ContestWeblinkLastChangedBy')
    owner = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='ContestWeblinkOwner')
        
    def __str__(self):
        return "%s %s %s" % (self.name, self.contest.name, self.website)
    
    @property
    def website_url(self):
        if self.website.startswith('http'):
            return self.website
        else:
            return 'http://%s' % self.website
    
    def save(self):
        self.last_modified = datetime.now()
        super(ContestWeblink, self).save()
    
    class Meta:
        ordering = ['contest']   
        
                  
class ContestGroupWeblink(models.Model):
    """
    A link to a website for a contest group
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    contest_group = models.ForeignKey(ContestGroup, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    website = models.CharField(max_length=255)
    order = models.IntegerField(default=10)
    lastChangedBy = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='ContestGroupWeblinkLastChangedBy')
    owner = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='ContestGroupWeblinkOwner')
        
    def __str__(self):
        return "%s %s %s" % (self.name, self.contest_group.name, self.website)
    
    @property
    def website_url(self):
        if self.website.startswith('http'):
            return self.website
        else:
            return 'http://%s' % self.website
    
    def save(self):
        self.last_modified = datetime.now()
        super(ContestGroupWeblink, self).save()
    
    class Meta:
        ordering = ['contest_group']                        


class ContestEventWeblink(models.Model):
    """
    A link to a website for a contest event
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    contest_event = models.ForeignKey(ContestEvent, on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    website = models.CharField(max_length=255)
    order = models.IntegerField(default=10)
    lastChangedBy = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='ContestEventWeblinkLastChangedBy')
    owner = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='ContestEventWeblinkOwner')
        
    def __str__(self):
        return "%s %s %s" % (self.name, self.contest_event.name, self.website)
    
    @property
    def website_url(self):
        if self.website.startswith('http'):
            return self.website
        else:
            return 'http://%s' % self.website
    
    def save(self):
        self.last_modified = datetime.now()
        super(ContestEventWeblink, self).save()
    
    class Meta:
        ordering = ['contest_event']  

class CurrentChampion(models.Model):
    """
    Link to current champions of all contests.  Auto generated overnight by the results_batch script
    """
    created = models.DateTimeField(default=datetime.now,editable=False)
    contest = models.ForeignKey(Contest, on_delete=models.PROTECT)
    contest_event = models.ForeignKey(ContestEvent, on_delete=models.PROTECT)
    band = models.ForeignKey(Band, on_delete=models.PROTECT)
    conductor = models.ForeignKey(Person, on_delete=models.PROTECT)
    

class ContestAchievementAward(models.Model):
    """
    Awards to a band about a contest
    """
    created = models.DateTimeField(default=datetime.now,editable=False)
    contest = models.ForeignKey(Contest, on_delete=models.PROTECT)
    contest_event = models.ForeignKey(ContestEvent, on_delete=models.PROTECT, blank=True, null=True)
    band = models.ForeignKey(Band, on_delete=models.PROTECT)
    band_name = models.CharField(max_length=100, blank=True, null=True)
    conductor = models.ForeignKey(Person, on_delete=models.PROTECT, blank=True, null=True)
    year_of_award = models.CharField(max_length=255)
    award = models.CharField(max_length=30)
    
    def __str__(self):
        return "[%s]%s in %s" % (self.award, self.band.name, self.year_of_award)
    
    class Meta:
        ordering = ['-year_of_award']  
    
    
class ContestProgrammeCover(models.Model):
    """
    An image of the contest programme cover
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    contest_group = models.ForeignKey(ContestGroup, blank=True, null=True, on_delete=models.PROTECT)
    contest = models.ForeignKey(Contest, blank=True, null=True, on_delete=models.PROTECT)
    event_date = models.DateField(help_text="Date of Event, DD/MM/YYYY")
    image = models.ImageField(upload_to='programme_cover/%Y')
    lastChangedBy = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='ContestProgrammeCoverLastChangedBy')
    owner = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='ContestProgrammeCoverOwner')
    
    def __str__(self):
        if self.contest_group:
            lContest = self.contest_group.name
        else:
            lContest = self.contest.name
        return "%s %s" % (lContest, self.event_date)
    
    def get_absolute_url(self):
        lReturn = '#'
        if self.contest_group:
            lReturn = "/contests/%s/%s/" % (self.contest_group.actual_slug, self.event_date.year)
        if self.contest:
            lReturn =  "/contests/%s/%s/" % (self.contest.slug, self.event_date)
        return lReturn
    
    def save(self):
        self.last_modified = datetime.now()
        super(ContestProgrammeCover, self).save()
        
    class Meta:
        ordering = ['contest_group', 'contest','event_date'] 
    
    
class ContestProgrammePage(models.Model):
    """
    A page from a contest programme
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    cover = models.ForeignKey(ContestProgrammeCover, on_delete=models.PROTECT)
    number = models.IntegerField(default=1)
    image = models.ImageField(upload_to='programme_page/%Y')
    description = models.CharField(max_length=255, blank=True, null=True)
    lastChangedBy = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='ContestProgrammePageLastChangedBy')
    owner = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='ContestProgrammePageOwner')
    
    def __str__(self):
        return "Programme Page"
    
    def save(self):
        self.last_modified = datetime.now()
        super(ContestProgrammePage, self).save()    
        
        
class ContestTestPiece(models.Model):
    """
    Support for adding additional test pieces to a contest
    """        
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    contest_event = models.ForeignKey(ContestEvent, on_delete=models.PROTECT)
    test_piece = models.ForeignKey(TestPiece, on_delete=models.PROTECT)
    AND_OR_CHOICES = (
                      ('and', 'and'),
                      ('or', 'or'),
                      )
    and_or = models.CharField(max_length=5, default="and", choices=AND_OR_CHOICES)
    lastChangedBy = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='ContestTestPieceLastChangedBy')
    owner = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='ContestTestPieceOwner')
    
    def __str__(self):
        return "%s %s %s" % (self.contest_event.contest.name, self.contest_event.date_of_event, self.test_piece.name)
    
    def save(self):
        self.last_modified = datetime.now()
        super(ContestTestPiece, self).save()
        
    class Meta:
        verbose_name_plural = 'Additional Contest Test Pieces'
        verbose_name = 'Additional Contest Test Piece'
        
        
class ContestTalkPage(models.Model):
    """
    A wiki page for superusers about the contest
    """    
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    lastChangedBy = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='ContestTalkPageLastChangedBy')
    owner = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='ContestTalkPageOwner')
    object_link = models.ForeignKey(Contest, on_delete=models.PROTECT)
    text = models.TextField()
    
    def save(self):
        self.last_modified = datetime.now()
        super(ContestTalkPage, self).save()
        
    def __str__(self):
        return "%s" % self.object_link.name
    
    def get_absolute_url(self):
        return "/contests/%s/talk/" % self.object_link.slug  
    
    
class GroupTalkPage(models.Model):
    """
    A wiki page for superusers about the contest group
    """    
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    lastChangedBy = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='ContestGroupTalkPageLastChangedBy')
    owner = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='ContestGroupTalkPageOwner')
    object_link = models.ForeignKey(ContestGroup, on_delete=models.PROTECT)
    text = models.TextField()
    
    def save(self):
        self.last_modified = datetime.now()
        super(GroupTalkPage, self).save()
        
    def __str__(self):
        return "%s" % self.object_link.name
    
    def get_absolute_url(self):
        return "/contests/%s/talk/" % self.object_link.slug.upper() 


class ResultPiecePerformance(models.Model):
    """
    A performance of a piece against a result
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    lastChangedBy = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='ResultPiecePerformanceLastChangedBy')
    owner = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='ResultPiecePerformanceOwner')
    result = models.ForeignKey(ContestResult, on_delete=models.PROTECT)
    piece = models.ForeignKey(TestPiece, on_delete=models.PROTECT)
    suffix = models.CharField(max_length=100, blank=True, null=True)
    ordering = models.IntegerField()
        
    def save(self):
        self.last_modified = datetime.now()
        super(ResultPiecePerformance, self).save()
        
    def __str__(self):
        return "%s - %s - %d - %s" % (self.result.contest_event.name, self.result.band_name, self.ordering, self.piece.name)
    
    def get_absolute_url(self):
        return "/contests/%s/talk/" % self.object_link.slug.upper() 
