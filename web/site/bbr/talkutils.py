# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from bands.models import BandTalkPage
from contests.models import ContestTalkPage, GroupTalkPage
from users.models import UserTalk

def _talk_sort(pValue):
    if pValue:
        return pValue.last_modified

def fetch_recent_talk_changes(request):
    """
    Return a list of recent talk page changes, ordered by date descending
    """
    lBandTalkPages = BandTalkPage.objects.all().order_by('-last_modified') 
    lContestTalkPages = ContestTalkPage.objects.all().order_by('-last_modified')
    lGroupTalkPages = GroupTalkPage.objects.all().order_by('-last_modified')
    lUserTalkPages = UserTalk.objects.all().order_by('-last_modified')

    lTalkPages = []
    for talk in lBandTalkPages:
        lTalkPages.append(talk)
    for talk in lContestTalkPages:
        lTalkPages.append(talk)
    for talk in lGroupTalkPages:
        lTalkPages.append(talk)
    for talk in lUserTalkPages:
        lTalkPages.append(talk)
        
    lReturn = sorted(lTalkPages, key=_talk_sort)
    lReturn.reverse()
    return lReturn[:20]
        
    