# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from django.contrib.auth.decorators import login_required
from django.http import Http404, HttpResponseRedirect

from bbr.render import render_auth
from contests.models import Contest, ContestGroup
from tags.forms import NewTagForm
from tags.models import ContestTag


def home(request):
    """
    Show list of all tags, with links to single_tag
    """
    lAllTags = ContestTag.objects.all()
    
    return render_auth(request, 'tags/home.html', {
                                                   'ContestTags' : lAllTags,
                                                  })


def single_tag(request, pTagSlug):
    """
    Show contests and contest groups linked to a single tag
    """
    try:
        lContestTag = ContestTag.objects.filter(slug=pTagSlug)[0]
    except IndexError:
        raise Http404
    
    lContests = Contest.objects.filter(tags=lContestTag)
    lContestGroups = ContestGroup.objects.filter(tags=lContestTag)
    
    return render_auth(request, 'tags/single_tag.html', {
                                                         'ContestTag': lContestTag,
                                                         'Contests' : lContests,
                                                         'ContestGroups' : lContestGroups,
                                                        })
    
@login_required
def new_tag(request):
    """
    Create a new tag if it doesn't already exist, and link it to the passed in group or contest
    """
    if request.user.profile.superuser == False and request.user.profile.regional_superuser == False:
        raise Http404
    
    lForm = NewTagForm(request.POST)
    if lForm.is_valid() == False:
        raise Http404
    lType = lForm.cleaned_data['type']
    lSlug = lForm.cleaned_data['slug']
    lTagName = lForm.cleaned_data['name'].strip()
    
    try:
        lTag = ContestTag.objects.filter(name__iexact=lTagName)[0]
    except IndexError:
        lTag = ContestTag()
        lTag.name = lTagName
        lTag.lastChangedBy = request.user
        lTag.owner = request.user
        lTag.save()
    
    if lType == 'group':
        try:
            lContestGroup = ContestGroup.objects.filter(slug=lSlug.lower())[0]
        except IndexError:
            raise Http404
        
        lContestGroup.tags.add(lTag)
        lContestGroup.save()

    elif lType == 'contest':
        try:
            lContest = Contest.objects.filter(slug=lSlug)[0]
        except IndexError:
            raise Http404
        
        lContest.tags.add(lTag)
        lContest.save()
    else:
        raise Http404
    
    
    return HttpResponseRedirect('/contests/%s/' % lSlug)
    
@login_required
def remove_tag(request, pTagSlug, pContestOrGroup, pContestOrGroupSlug):
    """
    Remove tag from a contest or group
    """
    if request.user.profile.superuser == False and request.user.profile.regional_superuser == False:
        raise Http404
    
    try:
        lTag = ContestTag.objects.filter(slug=pTagSlug)[0]
    except KeyError:
        raise Http404
    
    if pContestOrGroup == 'group':
        try:
            lContestGroup = ContestGroup.objects.filter(slug=pContestOrGroupSlug)[0]
        except IndexError:
            raise Http404
        
        lContestGroup.tags.remove(lTag)
        lContestGroup.save()
        
    elif pContestOrGroup == 'contest':
        try:
            lContest = Contest.objects.filter(slug=pContestOrGroupSlug)[0]
        except IndexError:
            raise Http404
        
        lContest.tags.remove(lTag)
        lContest.save()
    else:
        raise Http404
    
    if lTag.contest_set.count() == 0 and lTag.contestgroup_set.count() == 0:
        lTag.delete()
        return HttpResponseRedirect('/tags/')
    
    return HttpResponseRedirect('/tags/%s' % pTagSlug)