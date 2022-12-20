#!/home/bbr/.venv/bbr4/bin/python
# (c) 2012, 2018 Tim Sawyer, All Rights Reserved

import sys, os, re, time, shutil
from datetime import datetime, timedelta
from os.path import expanduser

os.environ['DJANGO_SETTINGS_MODULE'] = 'bbr.settingslive'

import django
django.setup()

from django.contrib.auth.models import User
from django.template.loader import render_to_string

from contests.models import ContestEvent, Venue
from bands.models import Band
from people.models import Person
from pieces.models import TestPiece

HOME = expanduser("~/web/bbr-data")

def write_file(filepath, filename, contents):
	filename = filename.replace('/', '_')
	os.makedirs(filepath, exist_ok=True)
	lFileToWrite = "%s/%s" % (filepath, filename)
	f = open(lFileToWrite, "w")
	f.write(contents)
	f.close()

def extract(list, dir, template, templateVar):
	print ("Extracting %d %s" % (list.count(), dir))
	shutil.rmtree(HOME + "/" + dir)
	lAllRows = list.all().order_by('name')
	for each in lAllRows:
		print ("\t%s" % each.name)
		try:
			lDir = each.slug[0:1]
		except IndexError:
			lDir = "_"
		lFilepath = "%s/%s/%s" % (HOME, dir, lDir)
		lFilename = "%s.xml" % each.slug
		lXml = render_to_string('extract/%s.xml' % template, { templateVar : each, })
		write_file(lFilepath, lFilename, lXml)
		time.sleep(0.1)

typeToGenerate = sys.argv[1]
print("Extracting with command line parameter" + typeToGenerate)

if typeToGenerate == "results":
	print ("Extracting %d Contest Events" % ContestEvent.objects.count())
	shutil.rmtree(HOME + "/Contest Events")
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
		time.sleep(0.1)

elif typeToGenerate == "bands":
	extract(Band.objects, "Bands", 'band', 'Band')

elif typeToGenerate == "people":
	extract(Person.objects, "People", 'person', 'Person')

elif typeToGenerate == "pieces":
	extract(TestPiece.objects, "Pieces", 'piece', 'Piece')

elif typeToGenerate == "venues":
	extract(Venue.objects, "Venues", 'venue', 'Venue')