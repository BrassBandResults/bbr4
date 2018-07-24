# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from bbr3.render import render_auth
from users.models import UserProfile


def home(request):
    """
    Show leaderboard
    """
    lLeaderboardTolerance = 50
    lUserProfiles = UserProfile.objects.exclude(user__is_superuser=True).filter(points__gte=lLeaderboardTolerance).order_by('-points').select_related()
    lNoPointsCount = UserProfile.objects.filter(points=0).count()
    lNotOnLeaderboardCount = UserProfile.objects.filter(points__gt=0, points__lt=lLeaderboardTolerance).count()
    lOnLeaderboardCount = lUserProfiles.count()
    return render_auth(request, 'leaderboard/home.html', {
                                                'Profiles' : lUserProfiles,
                                                'NoPointsCount' : lNoPointsCount,
                                                'NotOnLeaderboardCount' : lNotOnLeaderboardCount,
                                                'OnLeaderboardCount' : lOnLeaderboardCount,
                                              })

