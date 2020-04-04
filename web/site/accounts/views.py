# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

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
