# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from django.contrib import admin

from bbr3.admin import BbrAdmin
from pieces.models import TestPiece, TestPieceAlias, DownloadStore, DownloadAlbum, DownloadTrack


class TestPieceAliasInline(admin.TabularInline):
    model = TestPieceAlias

class TestPieceAdmin(BbrAdmin):
    prepopulated_fields = {"slug" : ("name",)}
    inlines = [TestPieceAliasInline]
    search_fields = ['name']
    
class DownloadStoreAdmin(BbrAdmin):
    search_fields = ['name',]

class DownloadTrackInline(admin.TabularInline):
    model = DownloadTrack
    exclude = 'band', 'band_name'

class DownloadAlbumAdmin(BbrAdmin):
    inlines = [DownloadTrackInline]
    search_fields = ['title',]
    list_display = ('title','type', 'band_name')
    
class DownloadTrackAdmin(BbrAdmin):
    search_fields = ['title',]

admin.site.register(TestPiece, TestPieceAdmin)
admin.site.register(DownloadStore, DownloadStoreAdmin)
admin.site.register(DownloadAlbum, DownloadAlbumAdmin)
admin.site.register(DownloadTrack, DownloadTrackAdmin)
