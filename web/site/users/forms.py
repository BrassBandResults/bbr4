# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved

from django import forms
from users.models import PersonalContestHistoryDateRange, UserTalk

        
class DateRangeForm(forms.ModelForm):
    start_date = forms.DateField(widget=forms.DateInput(format = '%d/%m/%Y'), input_formats=('%d/%m/%Y',))
    end_date = forms.DateField(widget=forms.DateInput(format = '%d/%m/%Y'), input_formats=('%d/%m/%Y',), required=False)
    
    class Meta:
        model = PersonalContestHistoryDateRange
        fields = ('band', 'start_date', 'end_date',)   
        
        
class PasswordResetForm(forms.Form):
    """
    Form used to enter username so password can be reset
    """
    username = forms.CharField(max_length=255)     
    
class NewEmailForm(forms.Form):
    """
    Form used to enter email when it is marked invalid
    """
    email_confirm = forms.EmailField() 
    email = forms.EmailField()
    
    def clean_email(self):
        lEmail = self.cleaned_data['email']
        lEmailConfirm = self.cleaned_data['email_confirm']
        if lEmail != lEmailConfirm:
            raise forms.ValidationError("The two emails didn't match.")
        return lEmail
    
class ResetPasswordForm(forms.Form):
    """
    Form used to enter new password
    """
    confirm_password = forms.CharField(max_length=255, widget=forms.PasswordInput())
    password = forms.CharField(max_length=255, widget=forms.PasswordInput())
    
    def clean_password(self):
        password1 = self.cleaned_data['password']
        password2 = self.cleaned_data['confirm_password']
        if password1 != password2:
            raise forms.ValidationError("The two password fields didn't match.")
        return password2
    
    
class UserTalkEditForm(forms.ModelForm):
    class Meta:
        model = UserTalk
        fields = ('text',)      