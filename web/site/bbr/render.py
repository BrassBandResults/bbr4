# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from django.shortcuts import render
from django.template import RequestContext
from django.conf import settings

def render_js(request, pTemplate, pParams=None):
    if pParams == None:
        pParams = {}
    return render(request, pTemplate, pParams, content_type='text/javascript')

def render_json(request, pTemplate, pParams=None):
    if pParams == None:
        pParams = {}
    return render(request, pTemplate, pParams, content_type='application/json')

def render_jsonp(request, pTemplate, pParams=None):
    if pParams == None:
        pParams = {}
    return render(request, pTemplate, pParams, content_type='text/javascript')    

def render_auth(request, pTemplate, pParams=None):
    if pParams == None:
        pParams = {}
    pParams["THUMBS_URL"] = settings.THUMBS_URL
    return render(request, pTemplate, pParams)