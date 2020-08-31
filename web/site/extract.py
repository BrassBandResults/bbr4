#!/home/bbr/.venv/bbr4/bin/python
# (c) 2012, 2018 Tim Sawyer, All Rights Reserved

import sys, os, re
from datetime import datetime, timedelta
from os.path import expanduser

os.environ['DJANGO_SETTINGS_MODULE'] = 'bbr.settingslive'

import django
django.setup()

from django.contrib.auth.models import User
from django.template.loader import render_to_string

from contests.models import ContestEvent

HOME = expanduser("~/web/bbr-data")

def write_file(filepath, filename, contents):
	filename = filename.replace('/', '_')
	os.makedirs(filepath, exist_ok=True)
	lFileToWrite = "%s/%s" % (filepath, filename)
	f = open(lFileToWrite, "w")
	f.write(contents)
	f.close()

print ("Extracting %d Contest Events" % ContestEvent.objects.count())
lAllEvents = ContestEvent.objects.all().order_by('-date_of_event')
lYear = None
for event in lAllEvents:
	if lYear != event.event_year:
		print (lYear)
		lYear = event.event_year
	print ("\t%s - %s" % (event.date_of_event, event.name))

	lFilepath = "%s/Contest Events/%d/%d/%d" % (HOME, event.date_of_event.year, event.date_of_event.month, event.date_of_event.day)
	lFilename = "%s.xml" % event.name
	lContestXml = render_to_string('extract/contest_event.xml', { 'ContestEvent' : event, })
	write_file(lFilepath, lFilename, lContestXml)

print ("Extracting %d Bands" % Band.objects.count())
lAllBands = Band.objects.all().order_by('name')
for band in lAllBands:
	print ("\t%s" % band.name)
	try:
		lDir = band.slug[0:1]
	except IndexError:
		lDir = "_"
	lFilepath = "%s/Bands/%s" % (HOME, lDir)
	lFilename = "%s.xml" % band.slug
	lBandXml = render_to_string('extract/band.xml', { 'Band' : band, })
	write_file(lFilepath, lFilename, lBandXml)
