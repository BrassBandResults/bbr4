# (c) 2009, 2012, 2015, 2018 Tim Sawyer, All Rights Reserved



import re

from django import forms
from django.forms import ModelForm

from bands.models import Band, BandTalkPage


CO_ORD_REGEX = "^\-?[0-9]+\.[0-9]+$"

class EditBandSuperuserForm(ModelForm):
    """
    Form for entering a new band, allows edit of website
    """
    class Meta:
        model = Band
        fields = ('name', 'region', 'postcode','latitude','longitude', 'rehearsal_night_1','rehearsal_night_2', 'website', 'twitter_name', 'contact_email', 'status', 'first_parent', 'second_parent', 'start_date', 'end_date', 'scratch_band', 'notes')

    def clean_latitude(self):
        """
        Validate latitude is in correct format
        """
        lLatitude = self.cleaned_data['latitude']
        lValue = lLatitude.strip()
        if lValue:
            lRegEx = re.compile(CO_ORD_REGEX) 
            if lRegEx.match(lValue) == None:
                raise forms.ValidationError("Please enter the location in decimal notation, for example 53.768761  If it ends with N it's positive, if S, then it's negative.")
            return lLatitude
    
    def clean_longitude(self):
        """
        Validation longitude is in correct format
        """
        lLongitude = self.cleaned_data['longitude']
        lValue = lLongitude.strip()
        if lValue:
            lRegEx = re.compile(CO_ORD_REGEX) 
            if lRegEx.match(lValue) == None:
                raise forms.ValidationError("Please enter the location in decimal notation, for example -1.82182  If it ends with E it's positive, if W, then it's negative.")
            return lLongitude


class EditBandForm(EditBandSuperuserForm):
    """
    Form for entering a new band, prevents edit of website
    """
    class Meta(EditBandSuperuserForm.Meta):
        exclude = ('website', 'twitter_name', 'first_parent', 'second_parent', 'start_date', 'end_date', 'website_news_page', 'website_contact_page')
        
        
class BandTalkEditForm(forms.ModelForm):
    class Meta:
        model = BandTalkPage
        fields = ('text',)    
        
        
