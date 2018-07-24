# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved



from django import forms

class UserMessageForm(forms.Form):
    title = forms.CharField(max_length=255)
    text = forms.CharField(widget=forms.Textarea(attrs={'width':"100%", 'cols' : "80", 'rows': "20", }))
    
