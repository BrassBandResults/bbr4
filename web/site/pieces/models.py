# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved



from datetime import datetime
import json

from django.contrib.auth.models import User
from django.db import models

from people.models import Person

class TestPiece(models.Model):
    """
    A test piece
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    name = models.CharField(max_length=100)
    year = models.CharField(max_length=10, default='', blank=True, null=True)
    slug = models.SlugField()
    composer = models.ForeignKey(Person, blank=True, null=True, related_name='ComposerPerson', on_delete=models.PROTECT)
    arranger = models.ForeignKey(Person, blank=True, null=True, related_name='ArrangerPerson', on_delete=models.PROTECT)
    CATEGORY_CHOICES = (
                        ('TestPiece', 'Test Piece'),
                        ('March', 'March'),
                        ('Solo', 'Solo'),
                        ('Other', 'Other'),
                        )
    category = models.CharField(max_length=10, default='TestPiece', choices=CATEGORY_CHOICES)
    percussion_required = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    lastChangedBy = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='TestPieceLastChangedBy')
    owner = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='TestPieceOwner')
    
    def __str__(self):
        lName =  self.name
        if self.year:
            return "%s (%s)" % (lName, self.year)
        return "%s" % (lName)
    
    def get_absolute_url(self):
        return "/pieces/%s/" % self.slug   
    
    def asJson(self):
        lComposer = ""
        lArranger = ""
        if self.composer:
            lComposer = self.composer.name
        if self.arranger:
            lArranger = self.arranger.name
        lDict = {
                 'id' : self.id,
                 'name' : self.name,
                 'composer_name' : lComposer,
                 'arranger_name' : lArranger,
                 }
        return json.dumps(lDict) 
    
    @property
    def composerarranger(self):
        """
        Return first of composer or arranger
        """  
        if self.composer:
            return self.composer
        if self.arranger:
            return self.arranger
        return Person()
    
    def save(self):
        self.last_modified = datetime.now()
        super(TestPiece, self).save()
    
    class Meta:
        ordering = ['name']
        
        
class TestPieceAlias(models.Model):
    """
    An alternative name for a test piece
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    name = models.CharField(max_length=100)
    piece = models.ForeignKey(TestPiece, on_delete=models.CASCADE)
    lastChangedBy = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='TestPieceAliasLastChangedBy')
    owner = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='TestPieceAliasOwner')
    
    def __str__(self):
        return "%s: %s" % (self.name, self.piece.name)
    
    def get_absolute_url(self):
        return "/pieces/%s/" % self.piece.slug    
    
    @property
    def slug(self):
        return self.piece.slug
    
    def composerarranger(self):
        """
        Return first of composer or arranger
        """
        return self.piece.composerarranger()  
    
    def save(self):
        self.last_modified = datetime.now()
        super(TestPieceAlias, self).save()
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = 'Test piece aliases'
            
            
class DownloadStore(models.Model):
    """
    A web site selling test piece downloads
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    name = models.CharField(max_length=50)
    link = models.URLField()
    lastChangedBy = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='DownloadStoreLastChangedBy')
    owner = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='DownloadStoreOwner')
    
    def __str__(self):
        return "%s" % (self.name)
    
    def save(self):
        self.last_modified = datetime.now()
        super(DownloadStore, self).save()        
        
        
class DownloadAlbum(models.Model):
    """
    An album available for download
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    store = models.ForeignKey(DownloadStore, on_delete=models.PROTECT)
    band = models.ForeignKey("bands.Band", on_delete=models.PROTECT, blank=True, null=True)
    band_name = models.CharField(max_length=100)
    title = models.CharField(max_length=50)
    link = models.URLField()
    thumbnail = models.ImageField(upload_to='cd_covers/%Y')
    TYPE_CHOICES = (
                    ('cd','Purchase CD'),
                    ('download', 'Download Track'),
                    )
    type = models.CharField(max_length=10, choices=TYPE_CHOICES, default='download')
    lastChangedBy = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='DownloadAlbumLastChangedBy')
    owner = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='DownloadAlbumOwner')
    
    def __str__(self):
        return "%s" % (self.title)
    
    def save(self):
        self.last_modified = datetime.now()
        super(DownloadAlbum, self).save() 
          
    
class DownloadTrack(models.Model):
    """
    A track on an album available for download
    """
    last_modified = models.DateTimeField(default=datetime.now,editable=False)
    created = models.DateTimeField(default=datetime.now,editable=False)
    album = models.ForeignKey(DownloadAlbum, on_delete=models.PROTECT)
    title = models.CharField(max_length=100)
    test_piece = models.ForeignKey(TestPiece, on_delete=models.PROTECT)
    link = models.URLField(blank=True, null=True)
    band = models.ForeignKey("bands.Band", on_delete=models.PROTECT, blank=True, null=True)
    band_name = models.CharField(max_length=100, blank=True, null=True)
    lastChangedBy = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='DownloadTrackLastChangedBy')
    owner = models.ForeignKey(User, on_delete=models.PROTECT, editable=False, related_name='DownloadTrackOwner')
    
    def __str__(self):
        return "%s" % (self.title)
    
    @property
    def track_link(self):
        if self.link:
            return self.link
        return self.album.link
        
    @property
    def track_band_name(self):
        if self.band_name:
            return self.band_name
        if self.band:
            return self.band.name
        if self.album.band_name:
            return self.album.band_name
        return self.album.band.name
    
    def save(self):
        self.last_modified = datetime.now()
        super(DownloadTrack, self).save()    
    
