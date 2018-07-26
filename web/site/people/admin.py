# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from django.contrib import admin

from bbr.admin import BbrAdmin
from people.models import Person, PersonAlias, ClassifiedPerson, PersonRelation


class PersonRelationAdmin(BbrAdmin):
    raw_id_fields = ['source_person', 'relation_person']
    search_fields = ['source_person__first_names', 'source_person__surname', 'relation_person__first_names', 'relation_person__surname']

class PersonAliasInline(admin.TabularInline):
    model = PersonAlias

class PersonAdmin(BbrAdmin):
    prepopulated_fields = {"slug" : ("first_names", "surname")}
    inlines = [PersonAliasInline]
    search_fields = ['first_names', 'surname', 'suffix']
    
class ClassifiedPersonAdmin(BbrAdmin):
    list_filter = ('visible','show_on_homepage')
    list_display = ('__str__', 'owner', 'visible', 'show_on_homepage', 'created', 'last_modified')

admin.site.register(Person, PersonAdmin)
admin.site.register(PersonRelation, PersonRelationAdmin)
admin.site.register(ClassifiedPerson, ClassifiedPersonAdmin)
