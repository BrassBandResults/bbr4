# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved

from datetime import datetime
from random import Random

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save

from badges.models import Badge
from bands.models import Band
from classifieds.models import PlayerPosition
from contests.models import ContestResult
from regions.models import Region


def _generate_key():
    """
    Generate a password reset key
    """
    return _generate_random(40)


def _generate_random(pSize):
    """
    Generate a random string, where letters are taking from alternate sides of the keyboard
    """
    rng = Random()
    righthand = '23456qwertasdfgzxcvbQWERTASDFGZXCVB'
    lefthand = '789yuiophjknmYUIPHJKLNM'
    passwordLength = pSize
    password = ""
    for i in range(passwordLength):
        if i%2:
            password = password + rng.choice(lefthand)
        else:
            password = password + rng.choice(righthand)
    return password


class PointsAward(models.Model):
    """
    Log of points awarded
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    type = models.CharField(max_length=25)
    serial = models.IntegerField()
    points_awarded = models.IntegerField()
    old_points = models.IntegerField()
    new_points = models.IntegerField()
    TYPE_BAND_MAPPER = 'Band_Mapper'
    TYPE_VENUE_MAPPER = 'Venue_Mapper'
    TYPE_CONTEST_RESULT = 'ContestResult'
    TYPE_CONTEST_RESULT_DELETED = 'CR-Deleted'
    TYPE_FEEDBACK_CLAIM = 'FeedbackClaim'
    TYPE_FEEDBACK_CLAIM_RETURNED = 'FC-Deleted'
    
    def __str__(self):
        return "%s (%s:%d)" % (self.user.username, self.type, self.points_awarded)
    
    def save(self):
        self.last_modified = datetime.now()
        super(PointsAward, self).save()
        
    class Meta:
        ordering = ['-created']
        

class UserProfile(models.Model):
    """
    Additional user details
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    user = models.OneToOneField(User, on_delete=models.PROTECT, related_name="profile")
    points = models.IntegerField(default=0)
    display_name = models.CharField(max_length=30, blank=True)
    contest_history_visibility = models.CharField(max_length=10, blank=True, null=True)
    enhanced_functionality = models.BooleanField(default=False)
    pro_member = models.BooleanField(default=False)
    superuser = models.BooleanField(default=False)
    regional_superuser = models.BooleanField(default=False)
    regional_superuser_region = models.ForeignKey(Region, on_delete=models.PROTECT, blank=True, null=True)
    regional_superuser_regions = models.ManyToManyField(Region, related_name='regions', blank=True)
    band_1 = models.ForeignKey(Band, on_delete=models.PROTECT, blank=True, null=True, related_name='BandOne')
    position_1 = models.ForeignKey(PlayerPosition, on_delete=models.PROTECT, blank=True, null=True, related_name='PositionOne')
    band_2 = models.ForeignKey(Band, blank=True, null=True, related_name='BandTwo', on_delete=models.PROTECT)
    position_2 = models.ForeignKey(PlayerPosition, on_delete=models.PROTECT, blank=True, null=True, related_name='PositionTwo')
    RANKINGS_ACCESS = (
                       ('N','Normal Free'),
                       ('B','Basic Paid'),
                       ('F','Full Paid'),
                       )
    rankings_access = models.CharField(max_length=1, default="N", choices=RANKINGS_ACCESS)
    old_rankings_access = models.CharField(max_length=1, blank=True, null=True)
    rankings_log = models.TextField(default='', blank=True)
    paypal_id = models.CharField(max_length=20, default='', blank=True, null=True)
    new_email_required = models.BooleanField(default=False)
    instrument = models.ForeignKey(PlayerPosition, blank=True, null=True, on_delete=models.PROTECT)
    stripe_token = models.CharField(max_length=30, blank=True, null=True)
    stripe_email = models.CharField(max_length=100, blank=True, null=True)
    stripe_customer = models.CharField(max_length=100, blank=True, null=True)
    max_profile_count = models.IntegerField(default=1)
            
    def __str__(self):
        return "%s (%s)" % (self.user.username, self.points)
    
    def is_regional_superuser_region(self, pRegion):
        """
        return true if regional superuser can see passed region
        """
        if self.superuser:
            return True
        
        if self.regional_superuser:
            for region in self.regional_superuser_regions.all():
                if region.id == pRegion.id:
                    return True
        return False
    
    def award_points_and_save(self, pType, pSerial, pPoints):
        """
        Add specified number of points for specified object
        """
        lPointsAward = PointsAward()
        lPointsAward.type = pType
        lPointsAward.serial = pSerial
        lPointsAward.points_awarded = pPoints
        lPointsAward.old_points = self.points
        lNewValue = self.points + pPoints
        lPointsAward.new_points = lNewValue
        lUserProfile = UserProfile.objects.filter(id=self.id)[0]
        lUserToLookFor = lUserProfile.user.id
        lPointsAward.user = User.objects.filter(id=lUserToLookFor)[0]
        lPointsAward.save()
        
        self.points = lNewValue
        self.save()

       
    def remove_points_and_save(self, pSerial, pType):
        """
        Remove the points awarded for something
        """
        if pType == PointsAward.TYPE_CONTEST_RESULT:
            lRemoveType = PointsAward.TYPE_CONTEST_RESULT_DELETED
        elif pType == PointsAward.TYPE_FEEDBACK_CLAIM:
            lRemoveType = PointsAward.TYPE_FEEDBACK_CLAIM_RETURNED
        try:
            lPointsAward = PointsAward.objects.filter(type=pType, serial=pSerial)[0]
            lUser = lPointsAward.user
            lProfile = lUser.profile
            lProfile.points = lProfile.points - lPointsAward.points_awarded
            lProfile.save()
            lPointsAward.type=lRemoveType
            lPointsAward.save()
        except:
            # it went wrong.  Don't care really, we just don't remove the points.
            pass
        
    
    @property
    def reputation(self):
        return self.points
    
    def save(self):
        if self.rankings_access != self.old_rankings_access:
            self.rankings_log += "Rankings access changed to %s on %s\n" % (self.rankings_access, datetime.now())
            self.old_rankings_access = self.rankings_access
        
        self.last_modified = datetime.now()
        super(UserProfile, self).save()
        
    class Meta:
        ordering = ['user__username']
        
        
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create user profile for new users at save user time, if it doesn't already exist
    """
    if created:
        UserProfile(user=instance).save()
        
post_save.connect(create_user_profile, sender=User)
        
        
class PersonalContestHistory(models.Model):
    """
    Personal contest history of a user
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    result = models.ForeignKey(ContestResult, on_delete=models.PROTECT)
    STATUS_CHOICES = (
                      ('accepted', 'Accepted'),
                      ('pending', 'Pending'),
                      )
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default="accepted")
    instrument = models.ForeignKey(PlayerPosition, blank=True, null=True, on_delete=models.PROTECT)
            
    def __str__(self):
        return "%s %s - %s %s" % (self.user.username, self.result.contest_event.date_of_event, self.result.band_name, self.result.contest_event.contest.name)
    
    def save(self):
        self.last_modified = datetime.now()
        super(PersonalContestHistory, self).save()
        
    class Meta:
        ordering = ['-result__contest_event__date_of_event']
        
        
class PersonalContestHistoryDateRange(models.Model):
    """
    Personal contest history date range - prompt user with new results that match this range
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    band = models.ForeignKey(Band, on_delete=models.PROTECT)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    imported = models.BooleanField(default=False)
            
    def __str__(self):
        return "%s (%s)" % (self.user.username, self.band.name)
    
    def save(self):
        self.last_modified = datetime.now()
        super(PersonalContestHistoryDateRange, self).save()
        
    class Meta:
        ordering = ['start_date', 'user__username']
        
        
class PasswordReset(models.Model):
    """
    Record a password reset request.
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    ip = models.GenericIPAddressField(help_text='The ip address of the user requesting password reset')
    useragent = models.CharField(max_length=512, help_text='Details of the browser the user used to request the reset')
    key = models.CharField(max_length=50, help_text='The key passed to the client to reset the password.  Generated randomly')
    username = models.CharField(max_length=50, help_text='The user to reset when the key is passed in on the url')
    used = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return '%s : %s' % (self.username, self.ip)
    
    def generateKey(self):
        self.key = _generate_key()
        
    def save(self):
        self.last_modified = datetime.now()
        super(PasswordReset, self).save()       
        

class UserNotification(models.Model):
    """
    Rows in this table indicate that a user should be notified when an event happens on the site
    """ 
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    notify_user = models.ForeignKey(User, on_delete=models.PROTECT)
    type = models.CharField(max_length=100)
    name_match = models.CharField(max_length=50, blank=True, null=True, help_text="If not empty, only matches where the name of the thing being notified contains this string, case insensitive")
    TYPE_CHOICES = (
                    ('own','Send if Owner only'),
                    ('notown','Send if another user changes something you own'),
                    ('all','Send Always'),
                    )
    notify_type = models.CharField(max_length=6, choices=TYPE_CHOICES, default='all')
    enabled = models.BooleanField(default=True)
    
    def __str__(self):
        lText = '%s : %s' % (self.notify_user.username, self.type)
        if self.enabled:
            return lText
        else:
            return "(%s)" % lText 
    
    def save(self):
        self.last_modified = datetime.now()
        super(UserNotification, self).save()
        
        
class UserBadge(models.Model):
    """
    A badge awarded to a user
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    type = models.ForeignKey(Badge, on_delete=models.PROTECT)
    notified = models.BooleanField(default=False, help_text='True if user has been notified of badge')
    
    def __str__(self):
        return '%s : %s' % (self.user.username, self.type.name)
    
    def save(self):
        self.last_modified = datetime.now()
        super(UserBadge, self).save()
        
        
class UserIpAddress(models.Model):
    """
    An ip address that a user has logged in from
    """        
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    count = models.IntegerField(default=0)
    ip_address = models.GenericIPAddressField()
    username = models.CharField(max_length=50)
    
    def save(self):
        self.last_modified = datetime.now()
        self.count += 1
        super(UserIpAddress, self).save()
        
        
class UserTalk(models.Model):
    """
    A user's own talk page - editable by them, and visible to other superusers
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    owner = models.ForeignKey(User, on_delete=models.PROTECT)
    text = models.TextField()
    
    @property
    def lastChangedBy(self):
        return self.owner
    
    def save(self):
        self.last_modified = datetime.now()
        super(UserTalk, self).save()
        
    def get_absolute_url(self):
        return "/users/%s/talk/" % self.owner.username         