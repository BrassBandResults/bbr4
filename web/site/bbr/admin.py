# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from django.contrib import admin

class BbrAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'created', 'last_modified')
    buttons = []
    
    def save_model(self, request, obj, form, change):
        """
        Stamp the model as last changed by the current user
        Set the owner to the current user if it is a blank field
        """
        obj.lastChangedBy = request.user
        try:
            owner = obj.owner
        except:
            obj.owner = request.user
        obj.save()
        
    def save_formset(self, request, form, formset, change):
        """
        Stamp the model as last changed by the current user
        Set the owner to the current user if it is a blank field
        """
        instances = formset.save(commit=False)
        for instance in instances:
            instance.lastChangedBy = request.user
            try:
                owner = instance.owner
            except:
                instance.owner = request.user
            instance.save()
        formset.save_m2m()
        