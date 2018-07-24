# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved



from django.forms import ModelForm

from people.models import Person, ClassifiedPerson


class EditPersonForm(ModelForm):
    """
    Form for entering a new person
    """
    class Meta:
        model = Person
        fields = ('first_names', 'surname', 'suffix')
        
class EditPersonAsSuperuserForm(ModelForm):
    """
    Form for entering a new person as a superuser
    """
    class Meta:
        model = Person
        fields = ('first_names','surname','suffix', 'bandname','start_date','end_date', 'notes', 'deceased','email')
        
        
class EditClassifiedProfileForm(ModelForm):
    """
    Form for entering or editing a ClassifiedProfile
    """
    class Meta:
        model = ClassifiedPerson
        fields = ('title', 'qualifications', 'email', 'website', 'picture', 'home_phone', 'mobile_phone', 'address', 'profile')
        