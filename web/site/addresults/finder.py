# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved

# routines for finding bands and conductors in the database to match with

from datetime import date
import re

from django import forms
from django.conf import settings

from bands.models import Band, PreviousBandName
from bbr.siteutils import add_space_after_dot, add_dot_after_initial
from people.models import PersonAlias, Person


def _filter(pQuerySet, pEventDate):
    """
    Filter the provided query set discarding any objects where the date range is outside the event date
    """
    lReturn = []
    for result in pQuerySet:
        if result.start_date and result.start_date > pEventDate:
            continue
        if result.end_date and result.end_date < pEventDate:
            continue
        lReturn.append(result)
        
    return lReturn[0]

def find_band(pBandName, pContestEvent, pRecurse=False):
    """
    Find a band given a name
    """
    lBandName = pBandName
    lBaseBandSet = Band.objects.exclude(status=4)
    lBaseAliasSet = PreviousBandName.objects.exclude(band__status=4)
    
    if pContestEvent and pContestEvent.future():
        lBaseBandSet = lBaseBandSet.exclude(status=0)
        lBaseAliasSet = lBaseAliasSet.exclude(band__status=0)
    
    if pContestEvent:
        lDateOfEvent = pContestEvent.date_of_event
    else:
        lDateOfEvent = date.today()
    # look for exact band name, case insensitive
    try:
        lBands = lBaseBandSet.filter(name__iexact=lBandName)
        lBand = _filter(lBands, lDateOfEvent)
    except IndexError:
        lBand = None
        
    # Look for a band with an old band name that matches exactly, case insensitive
    if lBand == None:
        try:
            lBandPreviousNames = lBaseAliasSet.filter(old_name__iexact=lBandName)
            lBandPreviousName = _filter(lBandPreviousNames, lDateOfEvent)
            lBand = lBandPreviousName.band
        except IndexError:
            lBand = None
            
    # look for an exact band name, adding Band on the end, case insensitive
    lBandNamePlusBand = "%s Band" % lBandName
    if lBand == None:
        try:
            
            lBands = lBaseBandSet.filter(name__iexact=lBandNamePlusBand)
            lBand = _filter(lBands, lDateOfEvent)
        except IndexError:
            lBand = None
            
    # look for a band with an old band name that matches exactly with Band appended, case insensitive
    if lBand == None:
        try:
            lBandPreviousNames = lBaseAliasSet.filter(old_name__iexact=lBandNamePlusBand)
            lBandPreviousName = _filter(lBandPreviousNames, lDateOfEvent)
            lBand = lBandPreviousName.band
        except IndexError:
            lBand = None
        
    # look for a band with a name that contains the band we're looking for, plus a space, case insensitive
    lBandNamePlusSpace = "%s " % lBandName        
    if lBand == None:
        try:
            lBands = lBaseBandSet.filter(name__icontains=lBandNamePlusSpace)
            lBand = _filter(lBands, lDateOfEvent)
        except IndexError:
            lBand = None
            
    # look for a band with an old band name that contains the band we're looking for, plus a space, case insensitive
    if lBand == None:
        try:
            lBandPreviousNames = lBaseAliasSet.filter(old_name__icontains=lBandNamePlusSpace)
            lBandPreviousName = _filter(lBandPreviousNames, lDateOfEvent)
            lBand = lBandPreviousName.band
        except IndexError:
            lBand = None
    
    # look for a band that has a name that contains the band name, case insensitive
    if lBand == None:
        try:
            lBands = lBaseBandSet.filter(name__icontains=lBandName)
            lBand = _filter(lBands, lDateOfEvent)
        except IndexError:
            lBand = None
        
    # look for band that has an old band name that contains the band name, case insensitive
    if lBand == None:
        try:
            lBandPreviousNames = lBaseAliasSet.filter(old_name__icontains=lBandName)
            lBandPreviousName = _filter(lBandPreviousNames, lDateOfEvent)
            lBand = lBandPreviousName.band
        except IndexError:
            lBand = None
    
    if pRecurse == False and lBand == None:
        # we haven't retried yet
        if lBandName.endswith(' Band') == True:
            lNewBandName = lBandName[:-len(' Band')].strip()
            lBand = find_band(lNewBandName, pContestEvent, pRecurse=True)
        elif lBandName.rfind('Brassband') > -1:
            lNewBandName = lBandName.replace('Brassband', 'Brass Band')
            lBand = find_band(lNewBandName, pContestEvent, pRecurse=True) 
    
    if lBand == None and pRecurse == False:
        raise forms.ValidationError("Can&#39;t find band '%s'" % pBandName)
    
    return lBand


def find_conductor(pConductorName, pBand, pContestEvent):
    """
    Find a conductor given a name and a band
    """
    lConductor = None
    
    lConductorName = pConductorName
    # if there is no space after a full stop then add one
    lConductorName = add_space_after_dot(lConductorName)
    # if there is no dot after an initial then add one
    lConductorName = add_dot_after_initial(lConductorName)
    # get rid of double spaces
    lConductorName = lConductorName.replace("  ", " ")
    
    # get existing conductors for this band's results.
    lContestResults = pBand.contestresult_set.all().select_related('person_conducting')
    lConductorMatches = []
    lInitial = None
    lSurname = None
    lPreviousConductors = {}
    for result in lContestResults:
        lRegEx = '^(\w)\.\s(\w+)$'
        lMatches = re.match(lRegEx, lConductorName) 
        if lMatches != None:
            # if the conductor name is initial, full stop, space, name,
            lInitial = lMatches.group(1).strip()
            lSurname = lMatches.group(2).strip()
        lPreviousConductors[result.person_conducting.slug] = result.person_conducting
        # If one of those match the name we're looking for exactly, case insensitive, use that conductor
        if result.person_conducting.name.lower() == lConductorName.lower():
            lConductorMatches.append(result.person_conducting)
        elif lInitial and result.person_conducting.name.startswith(lInitial) and result.person_conducting.name.endswith(" %s" % lSurname):
            lConductorMatches.append(result.person_conducting)
            
    # get existing results conductor aliases.  If any of those contain the name we're looking for, case insensitive, use that conductor
    lAliases = PersonAlias.objects.filter(person__in=lPreviousConductors.values())
    for alias in lAliases:
        if alias.name.lower() == lConductorName.lower():
            lConductorMatches.append(alias.person)
        elif lInitial and alias.name.startswith(lInitial) and alias.name.endswith(" %s" % lSurname):
            lConductorMatches.append(alias.person)
                
    if lConductorMatches and len(lConductorMatches) > 0:
        try:
            lConductor = _filter(lConductorMatches, pContestEvent.date_of_event)
        except IndexError:
            pass
        
    if lConductor == None:
        lConductorSuffix = ''
        lLastSpace = lConductorName.rfind(' ')
        lSurname = lConductorName[lLastSpace:].strip()
        for lSuffix, lSuffixDescription in settings.SUFFIXES:
            if lSurname == lSuffix:
                lConductorSuffix = lSuffix
                lConductorName = lConductorName[:len(lConductorName)-len(lSuffix)-1]
                lLastSpace = lConductorName.rfind(' ')
                lSurname = lConductorName[lLastSpace:].strip()
        lFirstNames = lConductorName[:lLastSpace].strip() 
           
        # Look for a conductor with the exact name we're looking for, case insensitive
        try:
            lConductors = Person.objects.filter(combined_name__iexact=lConductorName)
            lConductor = _filter(lConductors, pContestEvent.date_of_event)
        except IndexError:
            pass
    
    # Look for a conductor alias with the exact name we're looking for, case insensitive
    if lConductor == None:
        try:
            lConductorAliases = PersonAlias.objects.filter(name__iexact=lConductorName)
            lConductorAlias = _filter(lConductorAliases, pContestEvent.date_of_event)
            lConductor = lConductorAlias.person
        except IndexError:
            pass
    
    if lConductor == None:
        lRegEx = '^(\w)\.\s(\w+)$'
        lMatches = re.match(lRegEx, lConductorName) 
        if lMatches != None:
            # if the conductor name is initial, full stop, space, name,
            lInitial = lMatches.group(1).strip()
            lSurname = lMatches.group(2).strip()
            lInitialPlusSpace = "%s. " % lInitial
            try:
                # look for conductor names that start with the initial and end with the surname, excluding those that start with initial plus a dot, plus a space
                lConductors = Person.objects.filter(first_names__istartswith=lInitial).filter(surname__iexact=lSurname).exclude(first_names__istartswith=lInitialPlusSpace)
                lConductor = _filter(lConductors, pContestEvent.date_of_event)
            except IndexError:
                lConductor = None
                
            if lConductor == None:
                # not found looking at conductors, try aliases
                try:
                    lConductorAliases = PersonAlias.objects.filter(name__istartswith=lInitial).filter(name__iendswith=lSurname).exclude(name__istartswith=lInitialPlusSpace)
                    lConductorAlias = _filter(lConductorAliases, pContestEvent.date_of_event)
                    lConductor = lConductorAlias.person
                except IndexError:
                    lConductor = None
        
    if lConductor == None:
        raise forms.ValidationError("Can&#39;t find conductor '%s'" % lConductorName)
    
    return lConductor
