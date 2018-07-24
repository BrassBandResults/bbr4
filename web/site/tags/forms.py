# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved



from django import forms

class NewTagForm(forms.Form):
    type = forms.CharField(max_length=10)
    slug = forms.CharField(max_length=255)
    name = forms.CharField(max_length=255)
