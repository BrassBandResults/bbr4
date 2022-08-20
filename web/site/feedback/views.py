# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved



from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import Http404, HttpResponseRedirect

from bbr.siteutils import browser_details
from bbr.render import render_auth
from contests.models import ContestEvent
from feedback.models import SiteFeedback, ClarificationRequest
from bbr.notification import notification


def feedback(request):
    """
    Feedback has been posted
    """
    if request.POST:
        try:
            lRawFeedbackText = request.POST['feedback']
            lUrl = request.POST['x_url']
            lOwnerId = request.POST['x_owner']
            lIp = request.META['REMOTE_ADDR']
            lBrowser = request.META['HTTP_USER_AGENT']
            lReferrer = request.META['HTTP_REFERER']
            lUser = request.user
        except:
            raise Http404()
        
        lOwner = None
        if lOwnerId:
            try:
                lOwner = User.objects.filter(id=lOwnerId)[0]
            except IndexError:
                lOwner = None
        
        try:
            lControlUrl = request.POST['url']
        except:
            return HttpResponseRedirect('/feedback/thanks/')
        
        if lUrl.find("brassbandresults") == -1 and lUrl.find('http://localhost') == -1:
            return HttpResponseRedirect('/feedback/thanks/')
        
        if len(lControlUrl) > 0:
            return HttpResponseRedirect('/feedback/thanks/')
        
        lTjsUser = User.objects.filter(username='tjs')[0]
        lFeedback = SiteFeedback()
        if lOwner == None:
            lOwner = lTjsUser 
            
        if lOwner.id == request.user.id:
            lOwner = lTjsUser
            
        if lOwner == lTjsUser:
            lFeedback.status = 'Queue'
            lOwnerEmail = None
        else:
            lFeedback.status = 'Outstanding'     
            lOwnerEmail = lOwner.email
        
        lFeedback.url = lUrl
        lFeedback.comment = lRawFeedbackText
        lFeedback.lastChangedBy = lOwner 
        lFeedback.owner = lOwner
        lFeedback.ip = lIp
        lFeedback.browser_id = lBrowser
        if lUser.is_anonymous:
            lFeedback.reporter = None
        else:
            lFeedback.reporter = lUser
            
        if len(lFeedback.comment.strip()) > 0:
            lFeedback.save("Feedback send to %s" % lOwner.username)
        
            lContext = { 
                        'Url' : lUrl,
                        'Referrer' : lReferrer,
                        }
            notification(None, lFeedback, 'feedback', 'feedback', 'new', request.user, browser_details(request), pDestination=lOwnerEmail, pAdditionalContext=lContext, pUrl=lUrl)
                
        lNextUrl = lUrl[len('http://'):]
        lNextUrl = lNextUrl[lNextUrl.find('/'):]
        return HttpResponseRedirect('/feedback/thanks/?next=%s' % lNextUrl) 
    else:
        raise Http404()
    

def thanks(request):
    """
    thanks screen for providing feedback
    """
    lUrl = ""
    try:
        lUrl = request.GET['next']
    except:
        pass
        
    return render_auth(request, 'feedback_thanks.html', {'FeedbackUrl' : lUrl})


def queue(request):
    """
    Show all unclaimed and new feedback
    """
    if request.user.is_anonymous == True:
        raise Http404
    if request.user.profile.superuser == False:
        raise Http404
    lFeedback = SiteFeedback.objects.filter(status='Queue')
    
    return render_auth(request, 'feedback_queue.html', {'Feedback' : lFeedback})


def admin_queue(request):
    """
    Show admin queue
    """
    if request.user.is_superuser == False:
        raise Http404
    
    lFeedback = SiteFeedback.objects.filter(status='Admin')
    
    return render_auth(request, 'feedback_queue_admin.html', {'Feedback' : lFeedback})


@login_required
def feedback_detail(request, pFeedbackSerial):
    """
    Show details of a single feedback
    """
    if request.user.profile.superuser == False:
        raise Http404
    
    try:
        lFeedback = SiteFeedback.objects.filter(id=pFeedbackSerial)[0]
    except IndexError:
        raise Http404
    
    if lFeedback.status == 'Admin' and not request.user.is_superuser:
        raise Http404
    
    return render_auth(request, 'feedback/feedback_detail.html', {'Feedback' : lFeedback})


@login_required
def feedback_for_ip(request, pIpAddress):
    """
    Show all feedback from specified ip address
    """
    if request.user.profile.superuser == False:
        raise Http404
    
    lFeedbackForIp = SiteFeedback.objects.filter(ip=pIpAddress)
    
    return render_auth(request, 'feedback/feedback_for_ip.html', {'Feedback' : lFeedbackForIp,
                                                                  'IpAddress' : pIpAddress,
                                                                  })
