# (c) 2019 Tim Sawyer, All Rights Reserved

import re

from django import forms

from bands.models import Band


CO_ORD_REGEX = "^\-?[0-9]+\.[0-9]+$"

class EditLocationForm(forms.ModelForm):
    class Meta:
        model = Band
        fields = ('postcode', 'latitude','longitude', 'rehearsal_night_1', 'rehearsal_night_2')
        
        
    def clean_latitude(self):
        """
        Validate latitude is in correct format
        """
        lLatitude = self.cleaned_data['latitude']
        lValue = lLatitude.strip()
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
        lRegEx = re.compile(CO_ORD_REGEX) 
        if lRegEx.match(lValue) == None:
            raise forms.ValidationError("Please enter the location in decimal notation, for example -1.82182  If it ends with E it's positive, if W, then it's negative.")
        return lLongitude

        
