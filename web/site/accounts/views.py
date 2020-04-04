# (c) 2020 Tim Sawyer, All Rights Reserved

from bbr.render import render_auth
from django.http import HttpResponseRedirect

def anti_spam(request):
    """
    Show anti spam check
    """
    if request.method != 'POST':
        return render_auth(request, 'accounts/spam_check.html')
    else:
        if request.POST['section'] == "bs":
            return HttpResponseRedirect("/acc/register/")
        else:
            return HttpResponseRedirect("/accounts/loginpro/")
