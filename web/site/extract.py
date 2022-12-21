#!/home/bbr/.venv/bbr4/bin/python
# (c) 2012, 2018 Tim Sawyer, All Rights Reserved

import sys, os, re, time, shutil
from datetime import datetime, timedelta, date
from os.path import expanduser
from pathlib import Path

os.environ['DJANGO_SETTINGS_MODULE'] = 'bbr.settingslive'

import django
django.setup()

from django.contrib.auth.models import User
from django.template.loader import render_to_string

from contests.models import ContestEvent, Venue, ContestGroup, ContestType, Contest
from bands.models import Band
from people.models import Person
from pieces.models import TestPiece
from tags.models import ContestTag

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
	shutil.rmtree(HOME + "/" + dir, True)
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
print("Extracting with command line parameter " + typeToGenerate)

era1 = date(2000, 1, 1)
era2 = date(1970, 1, 1)
era3 = date(1950, 1, 1)
era4 = date(1900, 1, 1)

if typeToGenerate == "results":
	era = sys.argv[2]
	if era == "1":
		events = ContestEvent.objects.filter(date_of_event__gte=era1)
	elif era == "2":
		events = ContestEvent.objects.filter(date_of_event__lt=era1).filter(date_of_event__gte=era2)
	elif era == "3":
		events = ContestEvent.objects.filter(date_of_event__lt=era2).filter(date_of_event__gte=era3)		
	elif era == "4":
		events = ContestEvent.objects.filter(date_of_event__lt=era3).filter(date_of_event__gte=era4)		
	elif era == "5":
		events = ContestEvent.objects.filter(date_of_event__lt=era4)
	else:
		print("Era only can be 1 to 5")
		print("Usage: extract results 1")
		events = None
	print ("Extracting %d Contest Events" % events.count())
	path = HOME + "/Results/%s" % era
	shutil.rmtree(path, True)
	Path(path).mkdir(parents=True, exist_ok=True)
	lAllEvents = events.order_by('-date_of_event')
	lYear = None
	for event in lAllEvents:
		if lYear != event.event_year:
			print (lYear)
			lYear = event.event_year
		print ("\t%s - %s" % (event.date_of_event, event.name))

		lFilepath = "%s/Results/%s/%d/%d/%d" % (HOME, era, event.date_of_event.year, event.date_of_event.month, event.date_of_event.day)
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

elif typeToGenerate == "tags":
	extract(ContestTag.objects, "Tags", "contest_tag", "ContestTag")	

elif typeToGenerate == "groups":
	extract(ContestGroup.objects, "Groups", "contest_group", "ContestGroup")		

elif typeToGenerate == "types":
	list = ContestType.objects
	dir = "Types"
	template = "contest_type"
	templateVar = "ContestType"
	print ("Extracting %d %s" % (list.count(), dir))
	shutil.rmtree(HOME + "/" + dir, True)
	lAllRows = list.all().order_by('name')
	for each in lAllRows:
		print ("\t%s" % each.name)
		name = each.name.lower().replace(' ','-').replace('(','-').replace(')','-').replace("&",'and').replace(',','')
		lFilepath = "%s/%s" % (HOME, dir)
		lFilename = "%s.xml" % name
		lXml = render_to_string('extract/%s.xml' % template, { templateVar : each, })
		write_file(lFilepath, lFilename, lXml)
		time.sleep(0.1)

elif typeToGenerate == "contests":
	extract(Contest.objects, "Contests", "contest", "Contest")		