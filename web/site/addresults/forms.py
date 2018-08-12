# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved



import datetime
import re

from django import forms
from django.forms import ModelForm

from addresults.finder import find_band, find_conductor
from bbr.siteutils import browser_details
from contests.models import ContestResult, Contest, UNPLACED_RESULTS_POSITION, DISQUALIFIED_RESULTS_POSITION, WITHDRAWN_RESULTS_POSITION
from bbr.notification import notification


class ContestNameForm(forms.Form):
    contest = forms.CharField(max_length=100)
        
    def clean_contest(self):
        """
        Can't contain slashes or start with a number.  This stops someone
        (like me) entering a date in here by mistake
        """
        lContestName = self.cleaned_data['contest']
        if lContestName.find('/') > 0:
            raise forms.ValidationError("Contest name cannot contain a slash.  Did you enter a date here by mistake?")
        if lContestName.strip()[0].isdigit():
            raise forms.ValidationError("Contest name cannot begin with a number.  Please enter just a contest name, 'European Open (Championship Section)' rather than a specific contest, '2nd European Open (Championship Section)'")
        lRegEx = "\d{4}"
        lMatches = re.search(lRegEx, lContestName)
        if lMatches:
            raise forms.ValidationError("Contest name cannot contain a year.  Please enter just a contest name, 'European Open (Championship Section)' rather than a specific contest, 'European Open 2008 (Championship Section)'")
        if len(lContestName.strip()) == 0:
            raise forms.ValidationError("Please enter the name of the contest, e.g. 'Yorkshire Area (Third Section)'")
        return lContestName
    
class ContestDateForm(forms.Form):
    ContestDate = forms.CharField(max_length=10)
    
    def clean_ContestDate(self):
        """
        Check it's a date of format DD/MM/YYYY. MM/YYYY or just YYYY
        """
        lContestDate = self.cleaned_data['ContestDate']
        lSlashCount = lContestDate.count('/')
        if lSlashCount == 0:
            lDay, lMonth, lYear = (1, 1, lContestDate)
        elif lSlashCount == 1:
            lDay = 1
            lMonth, lYear = lContestDate.split('/')
        elif lSlashCount == 2:
            lDay, lMonth, lYear = lContestDate.split('/')
        else:
            raise forms.ValidationError("Please enter a valid date in format DD/MM/YYYY, MM/YYYY or just YYYY")
        
        if len(lYear) < 4:
            raise forms.ValidationError("Please enter a valid date in format DD/MM/YYYY, MM/YYYY or just YYYY, with four digit year")
        try:
            lDate = datetime.date(int(lYear), int(lMonth), int(lDay))
        except:
            raise forms.ValidationError("Please enter a valid date in format DD/MM/YYYY, MM/YYYY or just YYYY")
        return lContestDate
        


class NotesForm(forms.ModelForm):
    notes = forms.CharField(widget=forms.Textarea(attrs={'width':"100%",
                                                         'cols' : "80",
                                                         'rows': "4",
                                                         }))
    class Meta:
        model = ContestResult
        fields = ('notes',)


class ResultsForm(forms.Form):
    results = forms.CharField(widget=forms.Textarea(attrs={'width':"100%",
                                                           'cols' : "80",
                                                           'rows': "20",
                                                           }))
    
    def _pre_process_name(self, pName):
        """
        Pre-process the band and conductor name.
        - If the name is all upper case and is longer than 8 characters, force title capitalization.  This avoids all upper case bands in the database.
        """
        lName = pName
        if len(lName) > 5:
            if lName.isupper() or lName.islower():
                lName = lName.title()
                
        #if lName.rstrip().endswith('.'):
        #    lName = lName.rstrip()[:-1]
 
        return lName
        
    def clean_results(self):
        self.processed_results = []
        lines = self.cleaned_data['results'].split('\n')
        for line in lines:
            if len(line.rstrip().lstrip()) == 0:
                continue
        
            # formats to support
            #1. Cory Band, Robert Childs (16)
            #2. Grimethorpe Colliery, A. Withington (9) 193
            #3. Brass Band Aeolus, Bastien Stil, 4
            #4. Carlton Main Frickley Colliery, Russell Gray, 20, 195
            #5. Fodens Richardson (Gary Cutt), 15, 191 points
            
            # üçéøå

            # lRegEx = '\s*(\d+)\.?\s+([\w\(\)&\'\-\. ]+),\s*([\w\.\'\- ]+)\s*[\(,]?\s*(\d+)\)?[\s,]*([\d\.]*)\s*\w*' 
            lRegEx = '\s*([\d\-WwDd]+)\.?\s+([\w\(\)&\'\-\. /]+)\s*,\s*([\w\.\'\- ]+)\s*[\(,]?\s*([\d\-]+)\)?[\s,]*([\d\.]*)\s*\w*'
            lMatches = re.compile(lRegEx, re.U).match(line)  #re.match(lRegEx, line)
            if lMatches == None:
                raise forms.ValidationError("Can't work out '%s', is there a comma missing?  Are there odd characters?" % (line))
            else:
                lPosition = None
                lPositionString = lMatches.group(1).strip()
                if lPositionString.upper() == 'W':
                    lPosition = WITHDRAWN_RESULTS_POSITION
                elif lPositionString.upper() == 'D':
                    lPosition = DISQUALIFIED_RESULTS_POSITION
                elif lPositionString == '-':
                    lPosition = UNPLACED_RESULTS_POSITION
                else:
                    lPosition = int(lPositionString)
                lBandName = self._pre_process_name(lMatches.group(2).strip())
                lConductorName = self._pre_process_name(lMatches.group(3).strip())
                lDraw = lMatches.group(4).strip()
                if lDraw == '-':
                    lDraw = 0
                if str(lDraw).endswith('-'):
                    lDraw = lDraw[:-1]
                lPoints = lMatches.group(5).strip()
                if lPoints and lPoints.endswith('.'):
                    lPoints = lPoints[:-1]
                if len(lPoints) == 0:
                    lPoints = None
                elif lPoints == '0':
                    lPoints = None
            
                lBand = find_band(lBandName, self.event)
                lConductor = find_conductor(lConductorName, lBand, self.event)
                
                self.processed_results.append({"Position" : lPosition,
                                               "BandName" : lBandName,
                                               "ConductorName" : lConductorName,
                                               "Draw" : lDraw,
                                               "Points" : lPoints,
                                               "Band" : lBand,
                                               "Conductor" : lConductor,
                                               })
                
    
    def save(self, request, pContestEvent):
        for result in self.processed_results:
            lContestResult = ContestResult()
            lContestResult.contest_event = pContestEvent
            lContestResult.band = result["Band"]
            lContestResult.results_position = result["Position"]
            lContestResult.band_name = result["BandName"]
            lContestResult.draw = result["Draw"]
            lContestResult.points = result["Points"]
            lContestResult.test_piece = None
            lContestResult.notes = ''
            lContestResult.person_conducting = result["Conductor"]
            lContestResult.conductor_name = result["ConductorName"]
            lContestResult.lastChangedBy = request.user
            lContestResult.owner = request.user
            lContestResult.save()
            
            notification(None, lContestResult, 'contests', 'contest_result', 'new', request.user, browser_details(request))


class ContestTypeForm(ModelForm):
    """
    Form for prompting for the contest type, where we don't know it already
    """
    class Meta:
        model = Contest
        fields = ('contest_type_link',)