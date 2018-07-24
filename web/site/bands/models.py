# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from datetime import datetime, timedelta, date

from django.contrib.auth.models import User
from django.contrib.gis.db import models as geomodels
from django.contrib.gis.geos.factory import fromstr
from django.db import models

from regions.models import Region


class Band(models.Model):
    """
    A brass band taking part in the rankings
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    name = models.CharField(max_length=100, help_text='Current name of band')
    slug = models.SlugField(unique=True)
    website = models.CharField(max_length=100, blank=True)
    REVIEW_CHOICES = (
                      (5, 'Wow'),
                      (4, 'Good'),
                      (3, 'Average'),
                      (2, 'Functional'),
                      (1, 'Rubbish'),
                      (-1, 'None'),
                      )
    website_review = models.IntegerField(blank=True, null=True, choices=REVIEW_CHOICES)
    twitter_name = models.CharField(max_length=100, blank=True, null=True)
    region = models.ForeignKey(Region)
    postcode = models.CharField(max_length=10, null=True, blank=True, help_text='Rehearsal room postcode')
    latitude = models.CharField(max_length=15, blank=True, null=True)
    longitude = models.CharField(max_length=15, blank=True, null=True) 
    map_location = geomodels.PointField(dim=3, blank=True, null=True, editable=False)
    point = geomodels.PointField(dim=3, geography=True, blank=True, null=True, editable=False)
    DAY_CHOICES = (
                   ('0', 'Sunday'),
                   ('1', 'Monday'),
                   ('2', 'Tuesday'),
                   ('3', 'Wednesday'),
                   ('4', 'Thursday'),
                   ('5', 'Friday'),
                   ('6', 'Saturday'),
                   )
    rehearsal_night_1 = models.CharField(max_length=2, blank=True, null=True, choices=DAY_CHOICES)
    rehearsal_night_2 = models.CharField(max_length=2, blank=True, null=True, choices=DAY_CHOICES)
    contact_email = models.EmailField(null=True, blank=True)
    website_news_page = models.CharField(max_length=200, blank=True, null=True, help_text="URL of page containing band news")
    website_contact_page = models.CharField(max_length=200, blank=True, null=True, help_text="URL of page containing band contact form")
    notes = models.TextField(blank=True, null=True)
    mapper = models.ForeignKey(User, editable=False, related_name='BandMapper', blank=True, null=True)
    first_parent = models.ForeignKey('Band', related_name='FirstParentBand', blank=True, null=True)
    second_parent = models.ForeignKey('Band', related_name='SecondParentBand', blank=True, null=True, help_text="Used for the parents when a band merges with another")
    start_date = models.DateField(blank=True, null=True, help_text="Date band started contesting (yyyy-mm-dd)")
    end_date = models.DateField(blank=True, null=True, help_text="Date band folded or merged (yyyy-mm-dd)")
    STATUS_CHOICES = (
                      (0, 'Extinct'),
                      (1, 'Competing'),
                      (2, 'Non-competing'),
                      (3, 'Youth'),
                      (4, 'Salvation Army'),
                      (5, 'Now a Wind Band'),
                      )
    status = models.IntegerField(blank=True, null=True, choices=STATUS_CHOICES)
    national_grading = models.CharField(max_length=20, blank=True, null=True)
    scratch_band = models.BooleanField(default=False)
    lastChangedBy = models.ForeignKey(User, editable=False, related_name='BandLastChangedBy')
    owner = models.ForeignKey(User, editable=False, related_name='BandOwner')
    objects = geomodels.GeoManager()
    
    def __str__(self):
        return "%s" % self.name
    
    @property
    def date_range_display(self):
        lReturn = ""
        if self.start_date and self.end_date:
            lReturn += ' [%d-%d]' % (self.start_date.year, self.end_date.year)
        elif self.start_date:
            lReturn += ' [%d-]' % (self.start_date.year)
        elif self.end_date:
            lReturn += ' [-%d]' % (self.end_date.year)
        return lReturn
            
    
    def get_absolute_url(self):
        return "/bands/%s/" % self.slug    
    
    def save(self):
        if self.latitude != None and len(self.latitude) > 0 and self.longitude != None and len(self.longitude) > 0:
            lString = 'POINT(%s %s)' % (self.longitude.strip(), self.latitude.strip())
            self.map_location = fromstr(lString)
            self.point = fromstr(lString)
        self.last_modified = datetime.now()
        super(Band, self).save()
        
    @property
    def section(self):
        if self.status == 0 or self.status == 2 or self.status == 4:
            return None
        lToday = datetime.now()
        lThreeYearsAgo = lToday - timedelta(days=366 * 3)
        lEndOfYear = date(year=lToday.year, month=12, day=31)
        try:
            lRecentResult = self.contestresult_set.filter(contest_event__contest__section__isnull=False).filter(contest_event__date_of_event__gte=lThreeYearsAgo).filter(contest_event__date_of_event__lte=lEndOfYear).order_by('-contest_event__date_of_event')[0]
            self.national_grading = lRecentResult.contest_event.contest.section.name
            if not self.status:
                self.status = 1
            self.save()
            return lRecentResult.contest_event.contest.section
        except IndexError:
            self._auto_update_status()
            return None
        
    def _auto_update_status(self):
        """
        If the latest result is ten years ago, and status is null, then set status to extinct
        """
        if self.status == None and self.website == 'http://':
            lToday = date.today()
            lTenYearsAgo = lToday - timedelta(days=366 * 10)
            try:
                lLatestResult = self.contestresult_set.all().select_related('contest_event')[0]
                if lLatestResult.contest_event.date_of_event < lTenYearsAgo:
                    self.status = 0
                    self.save()
            except IndexError:
                pass
        
    def map_icon_name(self):
        lReturn = "band"
        if self.status == 2:
            lReturn = "non_competing"
        elif self.status == 0:
            lReturn = "extinct"
        elif self.status == 3:
            lReturn = "youth"
        elif self.status == 4:
            lReturn = "sa"
        else:
            lSection = self.national_grading
            if lSection:
                lReturn = lSection.lower().replace(' ','_')
        return lReturn 
    
    def name_for_map_title(self):
        lName = self.name
        return lName.replace("'","\\'")
    
    def type_description(self):
        if self.status == 0:
            lReturn = "Extinct Band"
        elif self.status == 2:
            lReturn = "Non-competing Band"
        elif self.status == 3:
            lReturn = "Youth Band"
        elif self.status == 4:
            lReturn = "Salvation Army Band"
        else:
            lSection = self.national_grading
            if lSection:
                lReturn = "%s Section Band" % lSection
            else:
                lReturn = "Unknown Type"
        return lReturn
        
        
    def rehearsal_nights(self):
        """
        Return rehearsal nights as a string
        """
        lReturn = ""
        if self.rehearsal_night_1 and len(self.rehearsal_night_1) > 0:
            lReturn = Band.DAY_CHOICES[int(self.rehearsal_night_1)][1]
            if self.rehearsal_night_2:
                if len(self.rehearsal_night_2) > 0:
                    lReturn += ", %s" % Band.DAY_CHOICES[int(self.rehearsal_night_2)][1]
        return lReturn
        
    @property
    def website_url(self):
        if self.website.strip() == 'http://':
            return ''
        elif len(self.website.strip()) == 0:
            return ''
        else:
            return self.website
        
    @property
    def wins(self):
        return self.contestresult_set.exclude(contest_event__contest__group__group_type='W').exclude(contest_event__date_of_event__gt=date.today()).filter(results_position=1)
    
    @property
    def seconds(self):
        return self.contestresult_set.exclude(contest_event__contest__group__group_type='W').exclude(contest_event__date_of_event__gt=date.today()).filter(results_position=2) 
    
    @property
    def thirds(self):
        return self.contestresult_set.exclude(contest_event__contest__group__group_type='W').exclude(contest_event__date_of_event__gt=date.today()).filter(results_position=3)
    
    @property
    def top_six_not_win(self):
        return self.contestresult_set.exclude(contest_event__contest__group__group_type='W').exclude(contest_event__date_of_event__gt=date.today()).filter(results_position__gte=2, results_position__lte=6) 
    
    @property
    def results_with_placings(self):
        return self.contestresult_set.exclude(contest_event__contest__group__group_type='W').exclude(contest_event__date_of_event__gt=date.today()).filter(results_position__lt=999)
    
    def earliest_result(self):
        try:
            return self.contestresult_set.all().order_by('contest_event__date_of_event')[0]
        except IndexError:
            return None
    
    def latest_result(self):
        try:
            return self.contestresult_set.all().order_by('-contest_event__date_of_event')[0]
        except IndexError:
            return None  
    
    @property
    def unplaced(self):
        return self.contestresult_set.exclude(results_position__lt=7).exclude(contest_event__contest__group__group_type='W').exclude(contest_event__date_of_event__gt=date.today())

    def reverse_results(self, pFilterSlug=None):
        lResults = self.contestresult_set.exclude(contest_event__contest__group__group_type='W').order_by('contest_event__date_of_event').extra(select={
                                 'event_result_count' : "SELECT count(*) FROM contests_contestresult cr WHERE cr.contest_event_id=contests_contestresult.contest_event_id",
                                 'event_max_result' : "SELECT max(results_position) FROM contests_contestresult cr WHERE cr.contest_event_id=contests_contestresult.contest_event_id",
                                 'event_max_draw' : "SELECT max(draw) FROM contests_contestresult cr WHERE cr.contest_event_id=contests_contestresult.contest_event_id",
                                 'marked_complete' : "SELECT complete FROM contests_contestevent ce WHERE ce.id=contests_contestresult.contest_event_id",
                                 },)
        if pFilterSlug == None:
            lResultsToReturn = lResults.filter(results_position__lt=26)
        else:
            if pFilterSlug.upper() == pFilterSlug:
                # contest group filter
                lSlug = pFilterSlug.lower()
                lResultsToReturn = lResults.filter(contest_event__contest__group__slug=lSlug).filter(results_position__lt=26)
            else:
                # contest filter
                lResultsToReturn = lResults.filter(contest_event__contest__slug=pFilterSlug).filter(results_position__lt=26)
        for result in lResultsToReturn:
            result.bands_competing = "%d" % result.event_result_count
            result.complete = True
            if not result.marked_complete:
                if result.event_result_count <= 4:
                    result.complete = False
                
                if result.complete == False:
                    result.bands_competing = None
                elif result.event_result_count < 10:
                    result.bands_competing = "about %d" % result.event_result_count

        return lResultsToReturn
    
    def previous_band_names(self):
        return self.previousbandname_set.filter(hidden=False)
    
    def location(self):
        lLocation = "%s,%s" % (self.latitude.strip(), self.longitude.strip())
        return lLocation
    
    class Meta:
        ordering = ['name']
    
        
class PreviousBandName(models.Model):
    """
    A previous name for a brass band
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    old_name = models.CharField(max_length=100, help_text='Old band name')
    band = models.ForeignKey(Band, on_delete=models.deletion.CASCADE)
    alias_start_date = models.DateField(blank=True, null=True, help_text="Start date for this alias (yyyy-mm-dd)")
    alias_end_date = models.DateField(blank=True, null=True, help_text="End date for this alias (yyyy-mm-dd)")
    hidden = models.BooleanField(default=False)
    lastChangedBy = models.ForeignKey(User, editable=False, blank=True, null=True, related_name='PreviousBandNameLastChangedBy')
    owner = models.ForeignKey(User, editable=False, blank=True, null=True, related_name='PreviousBandNameOwner')
        
    def __str__(self):
        return "%s -> %s" % (self.old_name, self.band.name)
    
    def save(self):
        self.last_modified = datetime.now()
        super(PreviousBandName, self).save()
        
    @property
    def name(self):
        return self.old_name
        
    @property
    def start_date(self):
        if self.alias_start_date:
            return self.alias_start_date
        return self.band.start_date
    
    @property
    def end_date(self):
        if self.alias_end_date:
            return self.alias_end_date
        return self.band.end_date
    
    @property
    def slug(self):
        return self.band.slug
    
    class Meta:
        ordering = ['old_name']
        
class BandRelationship(models.Model):
    """
    A relationship between two bands
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    left_band = models.ForeignKey(Band, related_name="LeftBand", on_delete=models.deletion.PROTECT)
    left_band_name = models.CharField(max_length=100, blank=True)
    BAND_RELATIONSHIPS = (
                          ('parent','Is Parent Of'),
                          ('senior','Is Senior Band To'),
                          ('subsumed','Was Subsumed Into'),
                          ('split','Split From'),
                          ('scratch','Is Scratch Band From'),
                          ('reformed','Reformed As'),
                          )
    relationship = models.CharField(max_length=10, choices=BAND_RELATIONSHIPS)
    right_band = models.ForeignKey(Band, related_name="RightBand", on_delete=models.deletion.PROTECT)
    right_band_name = models.CharField(max_length=100, blank=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)
    lastChangedBy = models.ForeignKey(User, editable=False, related_name='BandRelationshipLastChangedBy')
    owner = models.ForeignKey(User, editable=False, related_name='BandRelationshipOwner')
    
    def __str__(self):
        return "%s ->[%s]-> %s" % (self.left_band.name, self.relationship, self.right_band.name)
    
    
class BandTalkPage(models.Model):
    """
    A wiki page for superusers about the band
    """    
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    lastChangedBy = models.ForeignKey(User, editable=False, related_name='BandTalkPageLastChangedBy')
    owner = models.ForeignKey(User, editable=False, related_name='BandTalkPageOwner')
    object_link = models.ForeignKey(Band, on_delete=models.deletion.CASCADE)
    text = models.TextField()
    
    def save(self):
        self.last_modified = datetime.now()
        super(BandTalkPage, self).save()
        
    def __str__(self):
        return "%s" % self.object_link.name
    
    def get_absolute_url(self):
        return "/bands/%s/talk/" % self.object_link.slug 
