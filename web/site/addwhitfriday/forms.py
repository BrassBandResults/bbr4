# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved



import datetime
import re

from django import forms

from addresults.finder import find_band, find_conductor
from bands.models import Band, PreviousBandName
from bbr.siteutils import browser_details
from contests.models import ContestResult, Contest, ContestGroup, \
    ContestEvent, LOWEST_SPECIAL_POSITION
from contests.tasks import notification as contest_notification
from people.models import Person


class ContestNameForm(forms.Form):
    contest = forms.ModelChoiceField(queryset=ContestGroup.objects.filter(group_type='W'), empty_label=None)
    
        
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
        if len(lYear) < 4:
            raise forms.ValidationError("Please enter a valid date in format DD/MM/YYYY, MM/YYYY or just YYYY, with four digit year")
        try:
            lDate = datetime.date(int(lYear), int(lMonth), int(lDay))
        except:
            raise forms.ValidationError("Please enter a valid date in format DD/MM/YYYY, MM/YYYY or just YYYY")
        return lContestDate
        



class ResultsForm(forms.Form):
    results = forms.CharField(widget=forms.Textarea(attrs={'width':"100%",
                                                           'cols' : "80",
                                                           'rows': "20",
                                                           }))
    event_1 = forms.ModelChoiceField(queryset=Contest.objects.none(), required=True)
    event_2 = forms.ModelChoiceField(queryset=Contest.objects.none(), required=False)
    event_3 = forms.ModelChoiceField(queryset=Contest.objects.none(), required=False)
    event_4 = forms.ModelChoiceField(queryset=Contest.objects.none(), required=False)
    event_5 = forms.ModelChoiceField(queryset=Contest.objects.none(), required=False)
    event_6 = forms.ModelChoiceField(queryset=Contest.objects.none(), required=False)
    event_7 = forms.ModelChoiceField(queryset=Contest.objects.none(), required=False)
    event_8 = forms.ModelChoiceField(queryset=Contest.objects.none(), required=False)
    event_9 = forms.ModelChoiceField(queryset=Contest.objects.none(), required=False)
    event_10 = forms.ModelChoiceField(queryset=Contest.objects.none(), required=False)
    event_11 = forms.ModelChoiceField(queryset=Contest.objects.none(), required=False)
    event_12 = forms.ModelChoiceField(queryset=Contest.objects.none(), required=False)
    entering_points = forms.BooleanField(required=False)
    
    def __init__(self, pContestGroup, *args, **kwargs):
        super(ResultsForm, self).__init__(*args, **kwargs)
        self.fields['event_1'].queryset = Contest.objects.filter(group=pContestGroup)
        self.fields['event_2'].queryset = Contest.objects.filter(group=pContestGroup)
        self.fields['event_3'].queryset = Contest.objects.filter(group=pContestGroup)
        self.fields['event_4'].queryset = Contest.objects.filter(group=pContestGroup)
        self.fields['event_5'].queryset = Contest.objects.filter(group=pContestGroup)
        self.fields['event_6'].queryset = Contest.objects.filter(group=pContestGroup)
        self.fields['event_7'].queryset = Contest.objects.filter(group=pContestGroup)
        self.fields['event_8'].queryset = Contest.objects.filter(group=pContestGroup)
        self.fields['event_9'].queryset = Contest.objects.filter(group=pContestGroup)
        self.fields['event_10'].queryset = Contest.objects.filter(group=pContestGroup)
        self.fields['event_11'].queryset = Contest.objects.filter(group=pContestGroup)
        self.fields['event_12'].queryset = Contest.objects.filter(group=pContestGroup)
        
        
    def clean(self):
        self.processed_results = []
        lines = self.cleaned_data['results'].split('\n')
        for line in lines:
            if len(line.rstrip().lstrip()) == 0:
                continue
        
            # formats to support
            #Fairey's, 0, 5, 1, 1, 2, 2, 2, 1, 3, 1, 1
                       
            lRegEx = '\s*([\w\d\(\)&\'\-\. ]+)\s*,\s*((\d+\s*,\s*)+)\s*'
            lMatches = re.match(lRegEx, line)
            if lMatches == None:
                raise forms.ValidationError("Can't work out '%s', is there a comma missing?  Are there odd characters?" % (line))
            else:
                lBandName = lMatches.group(1).strip()
                lResults = lMatches.group(2).strip()
                lIndividualResults = lResults.split(',')
                lTabulatedResults = {}
                try:
                    lContests = {}
                    lMaxContest = 0
                    if self.cleaned_data['event_1']:
                        lTabulatedResults[self.cleaned_data['event_1'].slug] = lIndividualResults[0]
                        lContests[self.cleaned_data['event_1'].slug] = 'event1'
                        if lMaxContest < 1: lMaxContest = 1
                    if self.cleaned_data['event_2']:
                        lTabulatedResults[self.cleaned_data['event_2'].slug] = lIndividualResults[1]
                        lContests[self.cleaned_data['event_2'].slug] = 'event2'
                        if lMaxContest < 2: lMaxContest = 2
                    if self.cleaned_data['event_3']:
                        lTabulatedResults[self.cleaned_data['event_3'].slug] = lIndividualResults[2]
                        lContests[self.cleaned_data['event_3'].slug] = 'event3'
                        if lMaxContest < 3: lMaxContest = 3
                    if self.cleaned_data['event_4']:
                        lTabulatedResults[self.cleaned_data['event_4'].slug] = lIndividualResults[3]
                        lContests[self.cleaned_data['event_4'].slug] = 'event4'
                        if lMaxContest < 4: lMaxContest = 4
                    if self.cleaned_data['event_5']:
                        lTabulatedResults[self.cleaned_data['event_5'].slug] = lIndividualResults[4]
                        lContests[self.cleaned_data['event_5'].slug] = 'event5'
                        if lMaxContest < 5: lMaxContest = 5
                    if self.cleaned_data['event_6']:
                        lTabulatedResults[self.cleaned_data['event_6'].slug] = lIndividualResults[5]
                        lContests[self.cleaned_data['event_6'].slug] = 'event6'
                        if lMaxContest < 6: lMaxContest = 6
                    if self.cleaned_data['event_7']:
                        lTabulatedResults[self.cleaned_data['event_7'].slug] = lIndividualResults[6]
                        lContests[self.cleaned_data['event_7'].slug] = 'event7'
                        if lMaxContest < 7: lMaxContest = 7
                    if self.cleaned_data['event_8']:
                        lTabulatedResults[self.cleaned_data['event_8'].slug] = lIndividualResults[7]
                        lContests[self.cleaned_data['event_8'].slug] = 'event8'
                        if lMaxContest < 8: lMaxContest = 8
                    if self.cleaned_data['event_9']:
                        lTabulatedResults[self.cleaned_data['event_9'].slug] = lIndividualResults[8]
                        lContests[self.cleaned_data['event_9'].slug] = 'event9'
                        if lMaxContest < 9: lMaxContest = 9
                    if self.cleaned_data['event_10']:
                        lTabulatedResults[self.cleaned_data['event_10'].slug] = lIndividualResults[9]
                        lContests[self.cleaned_data['event_10'].slug] = 'event10'
                        if lMaxContest < 10: lMaxContest = 10
                    if self.cleaned_data['event_11']:
                        lTabulatedResults[self.cleaned_data['event_11'].slug] = lIndividualResults[10]
                        lContests[self.cleaned_data['event_11'].slug] = 'event11'
                        if lMaxContest < 11: lMaxContest = 11
                    if self.cleaned_data['event_12']:
                        lTabulatedResults[self.cleaned_data['event_12'].slug] = lIndividualResults[11]
                        lContests[self.cleaned_data['event_12'].slug] = 'event12'
                        if lMaxContest < 12: lMaxContest = 12
                except IndexError:
                    # droplist wasn't specified at a given position, we're done looking for results
                    pass
                
                if lMaxContest != len(lContests):
                    raise forms.ValidationError("Duplicate contest name found, please check the droplists specify unique contests.")
            
                lBand = find_band(lBandName, None)
                
                self.processed_results.append({"BandName" : lBandName,
                                               "Band" : lBand,
                                               "Results" : lResults,
                                               "TabulatedResults" : lTabulatedResults,
                                               "IndividualResults" : lIndividualResults
                                               })
                self.points_entered = self.cleaned_data['entering_points']
                
    
    def save(self, request, pContestEvent, pContestDate):
        for result in self.processed_results:
            lBand = result["Band"]
            lBandName = result["BandName"]
            lResults = result["TabulatedResults"]
            lUnknownConductor = Person.objects.filter(slug='unknown')[0]
            
            for contest_slug, position in lResults.items():
                position = position.strip()
                if len(position) == 0 or position == '0' or int(position) > LOWEST_SPECIAL_POSITION:
                    continue
                # create or find matching contest event
                lContest = Contest.objects.filter(slug=contest_slug)[0]
                try:
                    lContestEvent = ContestEvent.objects.filter(contest=lContest, date_of_event=pContestDate)[0]
                except IndexError:
                    lContestEvent = ContestEvent()
                    lContestEvent.contest = lContest
                    lContestEvent.date_of_event = pContestDate
                    lContestEvent.name = lContest.name
                    lContestEvent.lastChangedBy = request.user
                    lContestEvent.owner = request.user
                    lContestEvent.save()
                    
                # create result 
                lContestResult = ContestResult()
                lContestResult.contest_event = lContestEvent
                lContestResult.band = lBand
                if self.points_entered:
                    lContestResult.results_position = 0
                    lContestResult.points = position
                else:
                    lContestResult.results_position = position
                    lContestResult.points = 0
                lContestResult.band_name = lBandName
                lContestResult.draw = 0
                lContestResult.test_piece = None
                lContestResult.notes = ''
                lContestResult.person_conducting = lUnknownConductor
                lContestResult.lastChangedBy = request.user
                lContestResult.owner = request.user
                lContestResult.save()
                
                contest_notification(None, lContestResult, 'contest_result', 'new', request.user, browser_details(request))