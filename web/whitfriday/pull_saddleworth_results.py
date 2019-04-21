import requests
import re

YEAR = 2018


BASE_URL = "http://whitfriday.brassbands.saddleworth.org/Ranking_%s.php" % YEAR
OPTIONS_REGEX = '<option value="([ \w]+)">'
RESULTS_REGEX = '<tr><td>([\w]+)</td><td>&nbsp;([ \w]+)</td></tr>'
UPPERMILL_REGEX = '<tr><td>(Uppermill)\s+</td><td>&nbsp;([ \w]+)\s+</td></tr>'

list = requests.get(BASE_URL)
list_text = list.text
matches = re.findall(OPTIONS_REGEX, list_text)
for match in matches:
    lResultsString = "%s" % match
    r = requests.post("%s" % BASE_URL, data = {'band' : match})
    results_text = r.text
    matches = re.findall(RESULTS_REGEX, results_text)
    for match in matches:
        result = match[1]
        if result == " ": result = "0"
        lResultsString += ", %s" % result
    matches = re.findall(UPPERMILL_REGEX, results_text)
    for match in matches:
        result = match[1]
        if result == " ": result = "0"
        lResultsString += ", %s" % result

    print (lResultsString)
