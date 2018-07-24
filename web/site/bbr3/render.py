# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from django.shortcuts import render
from django.template import RequestContext

def render_auth(request, pTemplate, pParams=None):
    return render(request, pTemplate, pParams)