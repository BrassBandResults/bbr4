# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from bbr.render import render_auth
from badges.models import Badge

def home(request):
    """
    Show a list of all badges
    """
    lBadges = Badge.objects.all().extra(select={
                                 'count' : "SELECT count(*) FROM users_userbadge ub WHERE ub.type_id=badges_badge.id",
                                  },).order_by('count')
    return render_auth(request, 'badges/badges.html', {'Badges' : lBadges})