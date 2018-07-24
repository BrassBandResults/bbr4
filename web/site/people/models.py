# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from datetime import datetime, date

from django.conf import settings
from django.contrib.auth.models import User
from django.db import models

from sorl.thumbnail import ImageField


class Person(models.Model):
    """
    A conductor, adjudicator, composer or arranger
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    first_names = models.CharField(max_length=100,blank=True)
    surname = models.CharField(max_length=100,blank=True)
    suffix = models.CharField(max_length=10, blank=True, null=True, help_text='Jnr, Sr etc.', choices=settings.SUFFIXES)
    slug = models.SlugField(unique=True) # unique=True
    email = models.EmailField(null=True, blank=True)
    bandname = models.CharField(max_length=30, null=True, blank=True, help_text='Band this person is most associated with.  Only populate where duplicate conductor names')
    notes = models.TextField(blank=True, null=True)
    deceased = models.BooleanField(default=False)
    start_date = models.DateField(blank=True, null=True, help_text="Person won't be matched with things before this date (YYYY-MM-DD)")
    end_date = models.DateField(blank=True, null=True, help_text="Person won't be matched with things after this date (YYYY-MM-DD)")
    old_adjudicator_id = models.IntegerField(blank=True, null=True, help_text="The serial of this person as an adjudicator")
    old_conductor_id = models.IntegerField(blank=True, null=True, help_text="The serial of this person as a conductor")
    old_composer_id = models.IntegerField(blank=True, null=True, help_text="The serial of this person as a composer/arranger")
    old_adjudicator_slug = models.SlugField(blank=True, null=True, help_text="The slug of this person as an adjudicator")
    old_conductor_slug = models.SlugField(blank=True, null=True, help_text="The slug of this person as a conductor")
    old_composer_slug = models.SlugField(blank=True, null=True, help_text="The slug of this person as a composer/arranger")
    combined_name = models.CharField(max_length=200, blank=True, null=True, editable=False)
    profile_discount_code = models.CharField(max_length=30, default='', blank=True)
    lastChangedBy = models.ForeignKey(User, editable=False, related_name='PersonLastChangedBy')
    owner = models.ForeignKey(User, editable=False, related_name='PersonOwner')
    
    def __str__(self):
        lSuffix = ""
        if self.bandname:
            lSuffix = " (%s)" % self.bandname
        if self.suffix:
            lSuffix = " %s%s" % (self.suffix, lSuffix)
        return "%s, %s%s" % (self.surname, self.first_names, lSuffix)
    
    @property
    def name(self):
        if self.slug == 'unknown':
            return "Unknown"
        lSuffix = ""
        if self.suffix:
            lSuffix = " %s" % (self.suffix)
        return "%s %s%s" % (self.first_names, self.surname, lSuffix)
    
    @name.setter
    def name(self, pName):
        lLastSpace = pName.rfind(' ')
        if lLastSpace > 0:
            self.first_names = pName[:lLastSpace].strip()
            self.surname = pName[lLastSpace:].strip()
        else:
            self.surname = pName 
    
    def get_absolute_url(self):
        return "/people/%s/" % self.slug
    
    def reverse_results(self, pFilterSlug=None):
        lResultsToReturn = self.contestresult_set.exclude(contest_event__contest__group__group_type='W').filter(results_position__lt=26).extra(select={
                                 'event_result_count' : "SELECT count(*) FROM contests_contestresult cr WHERE cr.contest_event_id=contests_contestresult.contest_event_id",
                                 'event_max_result' : "SELECT max(results_position) FROM contests_contestresult cr WHERE cr.contest_event_id=contests_contestresult.contest_event_id",
                                 'event_max_draw' : "SELECT max(draw) FROM contests_contestresult cr WHERE cr.contest_event_id=contests_contestresult.contest_event_id",
                                 'marked_complete' : "SELECT complete FROM contests_contestevent ce WHERE ce.id=contests_contestresult.contest_event_id",
                                 },).order_by('contest_event__date_of_event')
        if pFilterSlug == None:
            lResultsToReturn = lResultsToReturn.filter(results_position__lt=26)
        else:
            if pFilterSlug.upper() == pFilterSlug:
                # contest group filter
                lSlug = pFilterSlug.lower()
                lResultsToReturn = lResultsToReturn.filter(contest_event__contest__group__slug=lSlug).filter(results_position__lt=26)
            else:
                # contest filter
                lResultsToReturn = lResultsToReturn.filter(contest_event__contest__slug=pFilterSlug).filter(results_position__lt=26)                                 
                                 
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
    
    @property
    def _base_results(self):
        lToday = date.today()
        return self.contestresult_set.exclude(contest_event__contest__group__group_type='W').exclude(contest_event__date_of_event__gt=lToday).exclude(results_position=10001) # Exclude withdrawn
    
    @property
    def wins(self):
        return self._base_results.filter(results_position=1)
    
    @property
    def seconds(self):
        return self._base_results.filter(results_position=2)
    
    @property
    def thirds(self):
        return self._base_results.filter(results_position=3)
    
    @property
    def top_six_not_win(self):
        return self._base_results.filter(results_position__gte=2, results_position__lte=6)

    @property
    def results_count(self):
        return self._base_results.count()
    
    @property
    def unplaced(self):
        return self._base_results.exclude(results_position__lte=6)
    
    @property
    def results_with_placings(self):
        return self._base_results.filter(results_position__lt=999)
    
    def earliest_result(self):
        try:
            return self._base_results.order_by('contest_event__date_of_event')[0]
        except IndexError:
            return None
        
    def latest_result(self):
        try:
            return self._base_results.order_by('-contest_event__date_of_event')[0]
        except IndexError:
            return None
       
    def save(self):
        self.last_modified = datetime.now()
        if self.suffix == None:
            self.suffix = ''
            
        lSlug = self.slug
        if len(lSlug) > 46:
            lSlug = lSlug[0:46]
        if not self.old_composer_slug:
            self.old_composer_slug = "%s-cmp" % lSlug
        if not self.old_adjudicator_slug:
            self.old_adjudicator_slug = "%s-adj" % lSlug
        if not self.old_conductor_slug:
            self.old_conductor_slug = "%s-cnd" % lSlug
            
        self.combined_name = "%s %s %s" % (self.first_names, self.surname, self.suffix)
        self.combined_name = self.combined_name.strip()
            
        super(Person, self).save()
    
    class Meta:
        ordering = ['surname','first_names', 'slug', 'bandname']   
        verbose_name_plural="People"     
        
        
class PersonRelation(models.Model):
    """
    A relation from one person to another
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    source_person = models.ForeignKey(Person, related_name="SourcePerson")
    relation_person = models.ForeignKey(Person, related_name="RelationPerson")
    relation = models.CharField(max_length=20)
    lastChangedBy = models.ForeignKey(User, editable=False, related_name='PersonRelationLastChangedBy')
    reverse_relation = models.CharField(max_length=20, blank=True, null=True) 
    owner = models.ForeignKey(User, editable=False, related_name='PersonRelationOwner')
    
    def __str__(self):
        return "%s --(%s)--> %s" % (self.source_person.name, self.relation, self.relation_person.name)
    
    def save(self):
        self.last_modified = datetime.now()
        super(PersonRelation, self).save()
            
        
class PersonAlias(models.Model):
    """
    Another name or mispelling for a person
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    name = models.CharField(max_length=100)
    person = models.ForeignKey(Person)
    hidden = models.BooleanField(default=True)
    lastChangedBy = models.ForeignKey(User, editable=False, related_name='PersonAliasLastChangedBy')
    owner = models.ForeignKey(User, editable=False, related_name='PersonAliasOwner')
        
    def __str__(self):
        return "%s (%s)" % (self.name, self.person.name)
    
    def save(self):
        self.last_modified = datetime.now()
        super(PersonAlias, self).save()
        
    @property
    def start_date(self):
        return self.person.start_date
    
    @property
    def end_date(self):
        return self.person.end_date
    
    @property
    def slug(self):
        return self.person.slug
    
    class Meta:
        ordering = ['name', 'person']        
        
        
        
class ClassifiedPerson(models.Model):
    """
    A classified profile of a person in the system
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    title = models.CharField(max_length=40, blank=True, default='', help_text="Title, i.e. Dr or Captain.  This will appear before the name.")
    qualifications = models.CharField(max_length=50, blank=True, help_text="Professional qualifications, i.e. BA (Hons).  These will appear after the name.")
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    home_phone = models.CharField(max_length=20, blank=True)
    mobile_phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    profile = models.TextField()
    picture = ImageField(blank=True, null=True, upload_to='profile_photos/%Y') 
    person = models.ForeignKey(Person, blank=True, null=True, on_delete=models.PROTECT)
    visible = models.BooleanField(default=False)
    show_on_homepage = models.BooleanField(default=True)
    lastChangedBy = models.ForeignKey(User, editable=False, related_name='ClassifiedPersonLastChangedBy')
    owner = models.ForeignKey(User, editable=False, related_name='ClassifiedPersonOwner')
    
    def __str__(self):
        return "%s" % self.person.name
    
    def get_absolute_url(self):
        return "/people/%s/" % self.person.slug
    
    @property
    def name(self):
        return self.person.name
    
    def email_mailbox(self):
        lMailbox, lDomain = self.email.split('@')
        return lMailbox
        
    def email_domain(self):
        lMailbox, lDomain = self.email.split('@')
        return lDomain
    
    def save(self):
        self.last_modified = datetime.now()
        super(ClassifiedPerson, self).save()
        
    class Meta:
        verbose_name_plural="Classified people"
        
        
        
        
        