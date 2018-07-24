# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved



import datetime

from django import forms

from contests.models import ContestResult, ContestEvent, Venue, Contest, \
    ContestProgrammeCover, ContestTalkPage, GroupTalkPage
from pieces.models import TestPiece


class ContestResultForm(forms.ModelForm):
    class Meta:
        model = ContestResult
        results_position = forms.CharField(widget=forms.HiddenInput())
        fields = ('results_position','band_name','draw','draw_second_part','points','points_first_part','points_second_part','points_third_part','points_fourth_part','penalty_points','notes')
        
        
class ContestEventForm(forms.ModelForm):
    venue_link = forms.ModelChoiceField(Venue.objects.all(), label='Venue', required=False)
    
    class Meta:
        model = ContestEvent
        fields = ('date_of_event', 'date_resolution', 'name', 'test_piece', 'notes', 'venue_link', 'complete', 'contest_type_override_link')   
                
        
class ContestForm(forms.ModelForm):
    class Meta:
        model = Contest
        fields = ('name','group', 'region','section','ordering','contest_type_link','qualifies_for', 'extinct', 'all_events_added', 'period')        
      
                
class FutureEventForm(forms.ModelForm):
    venue_link = forms.ModelChoiceField(Venue.objects.all(), label='Venue')
    date_of_event = forms.DateField(widget=forms.DateInput(format = '%d/%m/%Y'), 
                                    input_formats=('%d/%m/%Y',))

    def clean_date_of_event(self):
        """
        Check that date is in the future
        """
        lToday = datetime.date.today()
        if self.cleaned_data['date_of_event'] < lToday:
            raise forms.ValidationError("Future events must be given a date later than today")
        return self.cleaned_data['date_of_event']
    
    class Meta:
        model = ContestEvent
        fields = ('date_of_event', 'test_piece', 'venue_link')
        
        
class FutureEventFormNoContest(forms.ModelForm):
    contest = forms.ModelChoiceField(Contest.objects.all(), label='Contest')
    test_piece = forms.ModelChoiceField(TestPiece.objects.all(), label='Test Piece', required=False)
    venue_link = forms.ModelChoiceField(Venue.objects.all(), label='Venue', required=False)
    date_of_event = forms.DateField(widget=forms.DateInput(format = '%d/%m/%Y'), 
                                                           input_formats=('%d/%m/%Y',))

    def clean_date_of_event(self):
        """
        Check that date is in the future
        """
        lToday = datetime.date.today()
        if self.cleaned_data['date_of_event'] < lToday:
            raise forms.ValidationError("Future events must be given a date later than today")
        return self.cleaned_data['date_of_event']
    
    class Meta:
        model = ContestEvent
        fields = ('contest', 'date_of_event', 'test_piece', 'venue_link')        
        
        
class ContestProgrammeCoverForm(forms.ModelForm):
    event_date = forms.DateField(widget=forms.DateInput(format = '%d/%m/%Y'), 
                                                        input_formats=('%d/%m/%Y',))
    class Meta:
        model = ContestProgrammeCover
        fields = ('event_date','contest_group','contest','image') 
        
        
class ContestTalkEditForm(forms.ModelForm):
    class Meta:
        model = ContestTalkPage
        fields = ('text',)    
        
        
class GroupTalkEditForm(forms.ModelForm):
    class Meta:
        model = GroupTalkPage
        fields = ('text',)                    