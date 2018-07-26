# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import Http404, HttpResponseRedirect

from bbr.siteutils import browser_details
from bbr.render import render_auth
from usermessages.forms import UserMessageForm
from usermessages.models import Message
from usermessages.tasks import notification


@login_required
def show(request, pMessageSerial):
    """
    Show a single message, only if it is to the current user
    """
    lCurrentUser = User.objects.filter(username=request.user.username)[0]
    try:
        lMessage = Message.objects.filter(id=pMessageSerial).filter(to_user=lCurrentUser)[0]
    except:
        raise Http404()
    lMessage.read = True
    lMessage.save()
    return render_auth(request, 'messages/show.html', {"Message":lMessage})
    

@login_required    
def create(request, pUserCode):
    """
    Create a new message
    """
    return create_with_subject(request, pUserCode, '')
    
    
@login_required
def create_with_subject(request, pUserCode, pSubject):
    """
    Create a new message with a subject
    """
    lToUser = User.objects.filter(username=pUserCode)[0]
    if request.method == 'POST':
        lForm = UserMessageForm(request.POST)
        if lForm.is_valid():
            lMessage = Message()
            lMessage.from_user = User.objects.filter(username=request.user.username)[0]
            lMessage.to_user = lToUser
            lMessage.title = lForm.cleaned_data['title']
            lMessage.text = lForm.cleaned_data['text']
            lMessage.save()
            
            notification(None, lMessage, 'message', 'new', request.user, browser_details(request), pDestination=lMessage.to_user.email)
            
            return HttpResponseRedirect('/users/%s/' % lToUser.username)
    else:
        lForm = UserMessageForm(initial={'title' : pSubject, })
    return render_auth(request, 'messages/create.html', {"MessageForm":lForm, "To" : pUserCode})

@login_required
def delete(request, pMessageSerial):
    """
    Delete a message
    """
    lCurrentUser = User.objects.filter(username=request.user.username)[0]
    try:
        lMessage = Message.objects.filter(id=pMessageSerial).filter(to_user=lCurrentUser)[0]
    except:
        raise Http404()
    lMessage.deleted = True
    lMessage.save()
    return HttpResponseRedirect('/users/%s/' % lCurrentUser.username)
    
