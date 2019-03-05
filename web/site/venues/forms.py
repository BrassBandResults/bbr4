# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved

import re

from django import forms
from django.forms import ModelForm

from contests.models import Venue


CO_ORD_REGEX = "^\-?[0-9]+\.[0-9]+$"

class EditVenueForm(ModelForm):
    """
    Form for entering a new venue
    """
    class Meta:
        model = Venue
        fields = ('name', 'country', 'latitude','longitude', 'postcode', 'parent', 'notes')

    def clean_latitude(self):
        """
        Validate latitude is in correct format
        """
        lLatitude = self.cleaned_data['latitude']
        if lLatitude:
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
        if lLongitude:
            lValue = lLongitude.strip()
            if lValue:
                lRegEx = re.compile(CO_ORD_REGEX)
                if lRegEx.match(lValue) == None:
                    raise forms.ValidationError("Please enter the location in decimal notation, for example -1.82182  If it ends with E it's positive, if W, then it's negative.")
                return lLongitude
