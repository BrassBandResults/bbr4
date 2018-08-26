# (c) 2009, 2012, 2015, 2017 Tim Sawyer, All Rights Reserved

from datetime import date, datetime

from django.conf import settings
from django.contrib.auth import REDIRECT_FIELD_NAME, login as auth_login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.contrib.sites.shortcuts import get_current_site
from django.core.urlresolvers import reverse
from django.db import connection
from django.http import Http404, HttpResponseRedirect
from django.template import RequestContext
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_exempt, csrf_protect

from bbr.decorators import login_required_pro_user
from bbr.siteutils import browser_details
from bbr.render import render_auth
from bbr.talkutils import fetch_recent_talk_changes
from classifieds.models import PlayerPosition
from bbr.notification import notification 
from contests.models import ContestEvent, ContestResult
from feedback.models import SiteFeedback
from people.forms import EditClassifiedProfileForm
from people.models import ClassifiedPerson
from usermessages.models import Message
from users.forms import DateRangeForm, PasswordResetForm, ResetPasswordForm, NewEmailForm, UserTalkEditForm
from users.models import PersonalContestHistory, PersonalContestHistoryDateRange, UserProfile, PasswordReset, PointsAward, UserBadge, UserTalk, UserIpAddress

def user_contests_year(request, pUsername, pYear):
    """
    Create a table of results for a given year
    """    
    try:
        lUser = User.objects.filter(username=pUsername)[0]
    except IndexError:
        raise Http404()
    
    cursor = connection.cursor()
    lContestEvents = []
    lEventIds = ""
    lStartYear = date(int(pYear), 1, 1)
    lEndYear = date(int(pYear), 12, 31)
    cursor.execute("select event.date_of_event, event.name, contest.slug, contest.name, event.id, contest.id, event.date_resolution from contests_contest contest, contests_contestevent event WHERE event.owner_id = %(userid)s AND event.contest_id = contest.id AND event.date_of_event >= %(startyear)s AND event.date_of_event <= %(endyear)s order by event.date_of_event desc", {'userid' : lUser.id, 'startyear' : lStartYear, 'endyear' : lEndYear})
    rows = cursor.fetchall()
    for row in rows:
        lEvent = ContestEvent()
        lEvent.date_of_event = row[0]
        lEvent.name = row[1]
        lContestSlug = row[2]
        lEvent.contest_slug = lContestSlug
        lContestName = row[3]
        lEvent.id = row[4]
        lContestId = row[5]
        lEvent.date_resolution = row[6]
        if len(lEventIds) > 0:
            lEventIds += ','
        lEventIds += str(lEvent.id)
        lContestEvents.append(lEvent)
    cursor.close()
    return render_auth(request, "users/user_contests_year.htm", {
                                                                "User": lUser,
                                                                "ContestEvents" : lContestEvents,
                                                                })
    
@login_required
def user_list(request):
    """
    Show list of users
    """
    if request.user.is_superuser == False:
        raise Http404()
    
    lContestEventCounts = {}
    cursor = connection.cursor()
    cursor.execute("SELECT count(*),owner_id FROM contests_contestevent GROUP BY owner_id")
    rows = cursor.fetchall()
    for row in rows:
        lContestEventCounts[row[1]] = row[0]
    cursor.close()
    
    lContestResultCounts = {}
    cursor = connection.cursor()
    cursor.execute("SELECT count(*),owner_id FROM contests_contestresult GROUP BY owner_id")
    rows = cursor.fetchall()
    for row in rows:
        lContestResultCounts[row[1]] = row[0]
    cursor.close()
    
    lPersonalContestHistoryCounts = {}
    cursor = connection.cursor()
    cursor.execute("SELECT count(*),user_id FROM users_personalcontesthistory WHERE status = 'accepted' GROUP BY user_id")
    rows = cursor.fetchall()
    for row in rows:
        lPersonalContestHistoryCounts[row[1]] = row[0]
    cursor.close()
    
    lUserProfiles = UserProfile.objects.all().order_by('user__username').select_related('user')
    for profile in lUserProfiles:
        try:
            profile.event_count = lContestEventCounts[profile.user.id]
        except KeyError:
            profile.event_count = 0
            
        try:
            profile.result_count = lContestResultCounts[profile.user.id]
        except KeyError:
            profile.result_count = 0
            
        try:
            profile.history_count = lPersonalContestHistoryCounts[profile.user.id]
        except KeyError:
            profile.history_count = 0
            
    lUserCount = lUserProfiles.count()
    return render_auth(request, 'users/user_list.html', {'UserProfiles' : lUserProfiles,
                                                         "UserCount" : lUserCount})

@login_required
def feedback_done(request, pUsercode, pFeedbackId):
    """
    Mark feedback as done
    """
    try:
        lFeedback = SiteFeedback.objects.filter(id=pFeedbackId)[0]
    except IndexError:
        raise Http404()
    lFeedback.status = 'Done'
    lFeedback.lastChangedBy = request.user
    if request.user.id == lFeedback.owner.id:
        lFeedback.save("Feedback marked as done by %s" % request.user)
    return HttpResponseRedirect('/users/%s/' % pUsercode)


@login_required
def feedback_not_done(request, pUsercode, pFeedbackId):
    """
    Mark feedback as not done
    """
    try:
        lFeedback = SiteFeedback.objects.filter(id=pFeedbackId)[0]
    except IndexError:
        raise Http404()
    lFeedback.status = 'Outstanding'
    lFeedback.lastChangedBy = request.user
    if request.user.id == lFeedback.owner.id:
        lFeedback.save("Feedback marked as not done by %s" % request.user)
    return HttpResponseRedirect('/users/%s/' % pUsercode)


@login_required
@csrf_exempt
def feedback_inconclusive(request, pUsercode, pFeedbackId):
    """
    Mark feedback as inconclusive
    """
    if request.user.is_superuser == False:
        raise Http404
    try:
        lFeedback = SiteFeedback.objects.filter(id=pFeedbackId)[0]
    except IndexError:
        raise Http404()
    
    if request.POST:
        if not lFeedback.additional_comments:
            lFeedback.additional_comments = ""
        lFeedback.additional_comments += "\n"
        lFeedback.additional_comments += request.POST['extra']
    lFeedback.status = 'Inconclusive'
    lFeedback.lastChangedBy = request.user
    lFeedback.save("Feedback marked as inconclusive by %s with comment [%s]" % (request.user, request.POST['extra']))
    notification(None, lFeedback, 'feedback', 'feedback', 'inconclusive', request.user, browser_details(request))   
    return HttpResponseRedirect('/users/%s/' % pUsercode)


@login_required
def feedback_release_to_queue(request, pUsercode, pFeedbackId):
    """
    Release feedback into the queue
    """
    try:
        lFeedback = SiteFeedback.objects.filter(id=pFeedbackId)[0]
    except IndexError:
        raise Http404()
    
    lProfile = request.user.profile
    if lProfile.superuser and lFeedback.claim_date != None:
        lProfile.remove_points_and_save(lFeedback.id, PointsAward.TYPE_FEEDBACK_CLAIM)
    
    lFeedback.status = 'Queue'
    lFeedback.lastChangedBy = request.user
    lFeedback.claim_date = None
    if request.user.id == lFeedback.owner.id:
        lFeedback.save("Feedback queued by %s" % request.user)
        notification(None, lFeedback, 'feedback', 'feedback', 'to_queue', request.user, browser_details(request))   
    return HttpResponseRedirect('/users/%s/' % pUsercode)


@login_required
@csrf_exempt
def feedback_push_to_admin(request, pUsercode, pFeedbackId):
    """
    Release feedback to admin queue
    """
    try:
        lFeedback = SiteFeedback.objects.filter(id=pFeedbackId)[0]
    except IndexError:
        raise Http404()
    
    lProfile = request.user.profile
    if lProfile.superuser and lFeedback.claim_date != None:
        lProfile.remove_points_and_save(lFeedback.id, PointsAward.TYPE_FEEDBACK_CLAIM)
    
    lFeedbackComment = ""
    if request.POST:
        if not lFeedback.additional_comments:
            lFeedback.additional_comments = ""
        lFeedback.additional_comments += "\n"
        lFeedbackComment = request.POST['extra']
        lFeedback.additional_comments += lFeedbackComment
    lFeedback.status = 'Admin'
    lFeedback.lastChangedBy = request.user
    lFeedback.claim_date = None
    if request.user.id == lFeedback.owner.id:
        lFeedback.save("Feedback pushed to admin by %s with comment [%s]" % (request.user, lFeedbackComment))
        notification(None, lFeedback, 'feedback', 'feedback', 'to_admin', request.user, browser_details(request))   
    return render_auth(request, 'users/blank.html')


@login_required
def feedback_claim_from_queue(request, pUsercode, pFeedbackId):
    """
    Claim feedback from the queue
    """
    if request.user.profile.superuser == False:
        raise Http404()
    try:
        lFeedback = SiteFeedback.objects.filter(id=pFeedbackId)[0]
    except IndexError:
        raise Http404()
    lFeedback.status = 'Outstanding'
    lFeedback.owner = request.user
    lFeedback.lastChangedBy = request.user
    lFeedback.claim_date = datetime.now()
    lFeedback.save("Feedback claimed from queue by %s" % request.user)
    lProfile = request.user.profile
    if lProfile.superuser:
        notification(None, lFeedback, 'feedback', 'feedback', 'claim', request.user, browser_details(request))   
    return render_auth(request, 'users/blank.html')


@login_required
def maintain_date_ranges(request, pUsername):
    """
    Maintain the user's date ranges
    """
    if request.POST:
        lForm = DateRangeForm(request.POST)
        if lForm.is_valid():
            lDateRange = lForm.save(commit=False)
            lDateRange.user = request.user
            lDateRange.save()
            return HttpResponseRedirect('/users/%s/contesthistory' % pUsername)
    else:
        lForm = DateRangeForm()
    lUserDateRanges = PersonalContestHistoryDateRange.objects.filter(user=request.user)
    return render_auth(request, 'users/change_date_ranges.html', {"DateRanges" : lUserDateRanges,
                                                                  "form" : lForm})
    
@login_required
def delete_date_range(request, pUsername, pDateRangeSerial):
    """
    Delete a date range
    """
    try:
        lDateRange = PersonalContestHistoryDateRange.objects.filter(user=request.user, id=pDateRangeSerial)[0]
    except IndexError:
        raise Http404()
    lDateRange.delete()
    return HttpResponseRedirect('/users/%s/contesthistory/' % pUsername)


@login_required
def import_contests_date_range(request, pUsername, pDateRangeSerial):
    """
    Add the contests from the specified date range to the user's contest history
    """
    try:
        lDateRange= PersonalContestHistoryDateRange.objects.filter(user=request.user, id=pDateRangeSerial)[0]
    except IndexError:
        raise Http404()
    lResults = ContestResult.objects.filter(band=lDateRange.band, contest_event__date_of_event__gte=lDateRange.start_date)
    if lDateRange.end_date != None:
        lResults = lResults.filter(contest_event__date_of_event__lte=lDateRange.end_date)
    lCounter = 0
    for lEachResult in lResults:
        lPersonalContestHistory = PersonalContestHistory()
        lPersonalContestHistory.user = request.user
        lPersonalContestHistory.result = lEachResult
        lPersonalContestHistory.save()
        lCounter += 1
    lDateRange.imported = True
    lDateRange.save()
    
    return HttpResponseRedirect('/users/%s/contest_history/?count=%d' % (request.user.username, lCounter))


@login_required
def remove_contest_from_list(request, pUsername, pPersonalContestHistorySerial):
    """
    Remove a contest from the personal contest history list
    """
    try:
        lPersonalContestHistory = PersonalContestHistory.objects.filter(user=request.user, id=pPersonalContestHistorySerial)[0]
    except IndexError:
        raise Http404()
    lPersonalContestHistory.delete()
    return HttpResponseRedirect('/users/%s/contest_history/' % request.user.username)


@login_required
def approve_contest_in_list(request, pUsername, pPersonalContestHistorySerial):
    """
    Approve a pending entry from the personal contest history list
    """
    try:
        lPersonalContestHistory = PersonalContestHistory.objects.filter(user=request.user, id=pPersonalContestHistorySerial)[0]
    except IndexError:
        raise Http404()
    lPersonalContestHistory.status = 'accepted'
    lPersonalContestHistory.save()
    return HttpResponseRedirect('/users/%s/contest_history/' % request.user.username)


@login_required_pro_user
def set_instrument_in_list(request, pUsername, pPersonalContestHistorySerial, pPlayerPositionSerial):
    """
    Set the position played for a personal contest history list entry
    """
    try:
        lPersonalContestHistory = PersonalContestHistory.objects.filter(user=request.user, id=pPersonalContestHistorySerial)[0]
    except IndexError:
        raise Http404()
    
    try:
        lPlayerPosition = PlayerPosition.objects.filter(id=pPlayerPositionSerial)[0]
    except IndexError:
        raise Http404()
        
    lPersonalContestHistory.instrument = lPlayerPosition
    lPersonalContestHistory.save()
    
    return render_auth(request, 'blank.htm', {})


def forgotten_password(request):
    """
    Allow the user's password to be reset
    """
    if request.method == "POST":
        # send email with password reset in
        lForm = PasswordResetForm(request.POST)
        if lForm.is_valid():
            lPasswordReset = PasswordReset()
            lPasswordReset.generateKey()
            lPasswordReset.username = lForm.cleaned_data['username']
            lPasswordReset.ip = request.META['REMOTE_ADDR']
            lPasswordReset.useragent = request.META['HTTP_USER_AGENT']
            lPasswordReset.save() 
            try:
                lUser = User.objects.filter(username__iexact=lPasswordReset.username)[0]
            except:
                # try looking by email address
                try:
                    lUser = User.objects.filter(email__iexact=lPasswordReset.username).order_by('-last_login')[0]
                except:
                    # don't send email if account not found
                    return HttpResponseRedirect('/accounts/forgottenpassword/sent/')
    
            if lUser.is_active == False:
                # don't send email if user is inactive
                return HttpResponseRedirect('/accounts/forgottenpassword/sent/') 
    
            notification(lUser, lPasswordReset, 'users', 'password_reset', 'request', request.user, browser_details(request), pDestination=lUser.email) 
            return HttpResponseRedirect('/accounts/forgottenpassword/sent/')
    else:
        # show password reset form
        lForm = PasswordResetForm()
    return render_auth(request, "users/resetpassword/forgotten_password.html", {'form': lForm})


def forgotten_password_sent(request):
    """
    Inform the user that an email has been sent
    """
    return render_auth(request, "users/resetpassword/password_reminder_sent.html")

def reset_password(request, pResetKey):
    """
    Perform the password reset
    """
    try:
        lPasswordReset = PasswordReset.objects.filter(key=pResetKey)[0]
    except:
        raise Http404()
    
    try:
        lUserToReset = User.objects.filter(username__iexact=lPasswordReset.username)[0]
    except:
        # try looking by email address
        try:
            lUserToReset = User.objects.filter(email__iexact=lPasswordReset.username).order_by('-last_login')[0]
        except:
            # don't send email if account not found
            raise Http404()  

    if request.method == "POST":
        lForm = ResetPasswordForm(request.POST)
        if lForm.is_valid():
            lUserToReset.set_password(lForm.cleaned_data['password'])
            lUserToReset.save()
            lPasswordReset.used = datetime.now()
            lPasswordReset.save()
            
            notification(lPasswordReset, lUserToReset, 'users', 'password', 'changed', request.user, browser_details(request), pDestination=lUserToReset.email)
            
            return render_auth(request, "users/resetpassword/password_reset_done.html",  {'User' : lUserToReset,
                                                                                          'PasswordReset' : lPasswordReset,
                                                                                          'form' : lForm})    
    else:
        lForm = ResetPasswordForm()
    
    return render_auth(request, "users/resetpassword/password_reset_form.html", {'User' : lUserToReset,
                                                                                 'PasswordReset' : lPasswordReset,
                                                                                 'form' : lForm})


@login_required 
def edit_profile(request, pUsercode, pClassifiedProfileId):
    """
    Edit a classified profile
    """
    try:
        lProfile = ClassifiedPerson.objects.filter(owner=request.user, id=pClassifiedProfileId)[0]
    except IndexError:
        raise Http404
    
    if request.method == 'POST':
        lForm = EditClassifiedProfileForm(request.POST, request.FILES, instance=lProfile)
        if lForm.is_valid():
            lOldProfile = ClassifiedPerson.objects.filter(id=lProfile.id)[0]
            lNewProfile = lForm.save(commit=False)
            lNewProfile.lastChangedBy = request.user
            lNewProfile.owner = request.user
            lNewProfile.save()
            lNewProfile.check_expiry()
            
            notification(lOldProfile, lNewProfile, 'classifieds', 'profile', 'edit', request.user, browser_details(request))
            
            return HttpResponseRedirect('/users/%s/classifieds/' % (lProfile.owner.username))
    else:
        lForm = EditClassifiedProfileForm(instance=lProfile)
        
    return render_auth(request, 'classifieds/edit_profile.html', {'Profile' : lProfile,
                                                                  'form' : lForm,
                                                                  })   
    
    
@login_required 
def edit_band_profile(request, pUsercode, pClassifiedProfileId):
    """
    Edit a classified band profile
    """
    try:
        lProfile = ClassifiedBand.objects.filter(owner=request.user, id=pClassifiedProfileId)[0]
    except IndexError:
        raise Http404
    
    if request.method == 'POST':
        lForm = EditClassifiedBandForm(request.POST, request.FILES, instance=lProfile)
        if lForm.is_valid():
            lOldProfile = ClassifiedBand.objects.filter(id=lProfile.id)[0]
            lNewProfile = lForm.save(commit=False)
            lNewProfile.lastChangedBy = request.user
            lNewProfile.owner = request.user
            lNewProfile.save()
            lNewProfile.check_expiry()
            
            notification(lOldProfile, lNewProfile, 'classifieds', 'band_profile', 'edit', request.user, browser_details(request))
            
            return HttpResponseRedirect('/users/%s/classifieds/' % (lProfile.owner.username))
    else:
        lForm = EditClassifiedBandForm(instance=lProfile)
        
    return render_auth(request, 'classifieds/edit_band_profile.html', {'Profile' : lProfile,
                                                                       'form' : lForm,
                                                                       })    
         
    
@login_required
    
    
@login_required
def user_profile(request, pUsername):
    """
    Show profile for a user
    """
    try:
        lUser = User.objects.filter(username=pUsername)[0]
    except IndexError:
        raise Http404
    
    if request.user == lUser:
        return _show_owner_profile(request, lUser)
    else:
        return _show_public_profile(request, lUser)
    
    
def _show_public_profile(request, pUser):
    """
    Show user's public profile
    """
    lProfile = pUser.profile
        
    cursor = connection.cursor()
    lContestEvents = []
    lYears = {}
    lEventIds = ""
    cursor.execute("select event.date_of_event, event.name, contest.slug, contest.name, event.id, contest.id, event.date_resolution from contests_contest contest, contests_contestevent event where event.owner_id = '%s' and event.contest_id = contest.id order by event.date_of_event desc" % pUser.id)
    rows = cursor.fetchall()
    for row in rows:
        lEvent = ContestEvent()
        lEvent.date_of_event = row[0]
        lEvent.name = row[1]
        lContestSlug = row[2]
        lEvent.contest_slug = lContestSlug
        lContestName = row[3]
        lEvent.id = row[4]
        lContestId = row[5]
        lEvent.date_resolution = row[6]
        if len(lEventIds) > 0:
            lEventIds += ','
        lEventIds += str(lEvent.id)
        lYear = str(lEvent.date_of_event.year)
        try:
            lNewCount = lYears[lYear]["count"] + 1
            lYears[lYear] = {"year" : lYear, "count" : lNewCount}
        except KeyError:
            lYears[lYear] = {"year" : lYear, "count" : 1}
        lContestEvents.append(lEvent)
    cursor.close()
    
    cursor = connection.cursor()
    cursor.execute("select count(*) from contests_contestevent where owner_id = %s" % pUser.id)
    rows = cursor.fetchall()
    lContestsCount = rows[0][0]
    cursor.close()
    
    lPaginate=False
    if int(lContestsCount) > 30:
        lPaginate=True
        
    lYearNumbers = lYears.items()
    lYearNumbers.sort()
    lYearNumbers.reverse()
    lYears = [value for key, value in lYearNumbers]
        
    
    lContestHistory = None
    if lProfile.contest_history_visibility == 'public':
        lContestHistory = PersonalContestHistory.objects.filter(user=pUser, status='accepted').select_related()
    elif lProfile.contest_history_visibility == 'site':
        if request.user.is_anonymous() == False:
            lContestHistory = PersonalContestHistory.objects.filter(user=pUser, status='accepted').select_related()
            
    lUserBadges = UserBadge.objects.filter(user=pUser)
    for badge in lUserBadges:
        badge.type.name = badge.type.name.replace(' ', '&nbsp;')
    return render_auth(request, "users/public/user.html", {"User": pUser,
                                                    "ContestEvents" : lContestEvents,
                                                    "ContestCount" : lContestsCount,
                                                    "Paginate" : lPaginate,
                                                    "Years" : lYears,
                                                    "ContestHistory" : lContestHistory,
                                                    "Profile" : lProfile,
                                                    "UserBadges" : lUserBadges,
                                                    })
                    
def _get_tab_counts(request, pUser):
    """
    Return the counts to show on the profile tabs
    """  
    # Get feedback list to show  
    lOutstandingFeedback = SiteFeedback.objects.filter(owner__id=request.user.id, status="Outstanding").select_related().order_by('-created')
    lOutstandingFeedbackCount = lOutstandingFeedback.count()
    if lOutstandingFeedbackCount < 5:
        lOutstandingFeedbackCount = None

    # Sent feedback count        
    lSentFeedbackCount = SiteFeedback.objects.filter(reporter=request.user).select_related().order_by('created').count()
    if lSentFeedbackCount == 0:
        lSentFeedbackCount = None
        
    cursor = connection.cursor()
    cursor.execute("select count(*) from contests_contestevent where owner_id = %s" % pUser.id)
    rows = cursor.fetchall()
    lContestsCount = rows[0][0]
    cursor.close()
    
    lContestHistoryCount = PersonalContestHistory.objects.filter(user=request.user, status='accepted').select_related().count()
    lMessageCount = Message.objects.filter(to_user=request.user).filter(deleted=False).count()
    
    lUserBadges = UserBadge.objects.filter(user=pUser)
    for badge in lUserBadges:
        badge.type.name = badge.type.name.replace(' ', '&nbsp;')
    
    return lOutstandingFeedbackCount, lSentFeedbackCount, lContestsCount, lContestHistoryCount, lMessageCount, lUserBadges
    
    
def _show_owner_profile(request, pUser):
    """
    Show user's private profile
    """    
    lProfile = pUser.profile
    
    # default contest history visibility to private
    if lProfile.contest_history_visibility == None:
        lProfile.contest_history_visibility = 'private'
        lProfile.save()
        
    # Get feedback list to show  
    lOutstandingFeedback = SiteFeedback.objects.filter(owner__id=request.user.id, status="Outstanding").select_related().order_by('-created')
    
    lOutstandingFeedbackCount, lSentFeedbackCount, lContestsCount, lContestHistoryCount, lMessageCount, lUserBadges = _get_tab_counts(request, pUser)
    
    return render_auth(request, 'users/profile/user.html', {
                                                            'User' : pUser,
                                                            'Profile' : lProfile,
                                                            'Feedback' : lOutstandingFeedback,
                                                            'FeedbackCount' : lOutstandingFeedbackCount,
                                                            'SentFeedbackCount' : lSentFeedbackCount,
                                                            'ContestCount' : lContestsCount,
                                                            'PerformanceCount' : lContestHistoryCount, 
                                                            "MessageCount" : lMessageCount,
                                                            "UserBadges" : lUserBadges,
                                                            })
    
@login_required
def feedback_sent(request, pUsername):
    """
    Show feedback sent
    """
    try:
        lUser = User.objects.filter(username=pUsername)[0]
    except IndexError:
        raise Http404
    lProfile = lUser.profile
    
    if pUsername != lUser.username:
        raise Http404
    
    lSentFeedback = SiteFeedback.objects.filter(reporter=request.user).select_related().order_by('created')
    lOutstandingFeedbackCount, lSentFeedbackCount, lContestsCount, lContestHistoryCount, lMessageCount, lUserBadges = _get_tab_counts(request, lUser)
        
    return render_auth(request, 'users/profile/feedback_sent.html', {
                                                            'User' : lUser,
                                                            'Profile' : lProfile,
                                                            'SentFeedback' : lSentFeedback,
                                                            'FeedbackCount' : lOutstandingFeedbackCount,
                                                            'SentFeedbackCount' : lSentFeedbackCount,
                                                            'ContestCount' : lContestsCount,
                                                            'PerformanceCount' : lContestHistoryCount,
                                                            "MessageCount" : lMessageCount,
                                                            "UserBadges" : lUserBadges,
                                                            })
    
@login_required
def results_added(request, pUsername):
    """
    Show results that user has added
    """
    try:
        lUser = User.objects.filter(username=pUsername)[0]
    except IndexError:
        raise Http404
    lProfile = lUser.profile
    
    if pUsername != lUser.username:
        raise Http404
    
    lOutstandingFeedbackCount, lSentFeedbackCount, lContestsCount, lContestHistoryCount, lMessageCount, lUserBadges = _get_tab_counts(request, lUser)
        
    cursor = connection.cursor()
    lContestEvents = []
    lYears = {}
    lEventIds = ""
    cursor.execute("""
            SELECT event.date_of_event, 
                   event.name, 
                   contest.slug, 
                   contest.name, 
                   event.id, 
                   contest.id, 
                   event.date_resolution, 
                   event.complete, 
                   (select count(*) from contests_contestresult where contest_event_id=event.id),
                   (select count(*) from contests_contestresult where contest_event_id=event.id and results_position < 9000),
                   (select max(results_position) from contests_contestresult where contest_event_id=event.id and results_position < 9000),
                   (select count(*) from contests_contestresult where contest_event_id=event.id and person_conducting_id != %d),
                   (select count(*) from contests_contestresult where contest_event_id=event.id and draw > 0),
                   (select max(draw) from contests_contestresult where contest_event_id=event.id),
                   event.test_piece_id
            FROM contests_contest contest, 
                 contests_contestevent event 
            WHERE event.owner_id = '%s' 
            AND event.contest_id = contest.id
            ORDER BY event.date_of_event desc""" % (settings.UNKNOWN_PERSON_ID, lUser.id))
    rows = cursor.fetchall()
    for row in rows:
        lEvent = ContestEvent()
        lEvent.date_of_event = row[0]
        lEvent.name = row[1]
        lContestSlug = row[2]
        lEvent.contest_slug = lContestSlug
        lContestName = row[3]
        lEvent.id = row[4]
        lContestId = row[5]
        lEvent.date_resolution = row[6]
        lEvent.complete = row[7]
        lEvent.result_count = row[8]
        lEvent.positions_count = row[9]
        lEvent.max_position = row[10]
        lEvent.conductor_count = row[11]
        lEvent.draw_count = row[12]
        lEvent.max_draw = row[13]
        lEvent.test_piece_id = row[14]
        if len(lEventIds) > 0:
            lEventIds += ','
        lEventIds += str(lEvent.id)
        lYear = str(lEvent.date_of_event.year)
        try:
            lNewCount = lYears[lYear]["count"] + 1
            lYears[lYear] = {"year" : lYear, "count" : lNewCount}
        except KeyError:
            lYears[lYear] = {"year" : lYear, "count" : 1}
        lContestEvents.append(lEvent)
    cursor.close()
    
    lCompletelyComplete = True
    for row in lContestEvents:
        if row.complete == False:
            lCompletelyComplete = False
        
    
    return render_auth(request, 'users/profile/results_added.html', {
                                                            'User' : lUser,
                                                            'Profile' : lProfile,
                                                            "ContestCount" : lContestsCount,
                                                            "ContestEvents" : lContestEvents,
                                                            'FeedbackCount' : lOutstandingFeedbackCount,
                                                            'SentFeedbackCount' : lSentFeedbackCount,
                                                            'PerformanceCount' : lContestHistoryCount, 
                                                            "MessageCount" : lMessageCount,
                                                            "UserBadges" : lUserBadges,
                                                            "CompletelyComplete" : lCompletelyComplete,
                                                            })    
    
@login_required
def contest_history(request, pUsername):
    """
    Show results that user has performed in
    """
    try:
        lUser = User.objects.filter(username=pUsername)[0]
    except IndexError:
        raise Http404
    lProfile = lUser.profile
    
    if request.user.profile.superuser == False:
        if request.user != lUser:
            return HttpResponseRedirect("/users/%s/contest_history/" % request.user.username)
    
    if lProfile.contest_history_visibility == None:
        lProfile.contest_history_visibility = 'private'
        lProfile.save()
    
    lOutstandingFeedbackCount, lSentFeedbackCount, lContestsCount, lContestHistoryCount, lMessageCount, lUserBadges = _get_tab_counts(request, lUser)
        
    lContestHistory = PersonalContestHistory.objects.filter(user=lUser).select_related('user','result__band', 'result__person_conducting', 'result__contest_event', 'result__contest_event__contest', 'result__test_piece', 'result__contest_event__test_piece')
    lUserDateRanges = PersonalContestHistoryDateRange.objects.filter(user=lUser)
        
    if pUsername == request.user.username and request.POST:
        try:
            lPrivacy = request.POST['privacy']
            lProfile.contest_history_visibility = lPrivacy
            lProfile.save()
            return HttpResponseRedirect('/users/%s/contest_history/' % request.user.username)
        except KeyError:
            pass
        
    try:
        lCount = request.GET['count']
    except KeyError:
        lCount = None
            
    lResultsWithPositionCount = 0
    lWinsCount = 0
    lTopSixNotWinCount = 0
    lUnplacedCount = 0
    lHistoryBands = {}
    lHistoryConductors = {}
    lTotalPositions = 0.0
    for history in lContestHistory:
        lResultsPosition = history.result.results_position
        lHistoryBands[history.result.band_id] = history.result.band
        if history.result.person_conducting.slug != 'unknown':
            lHistoryConductors[history.result.person_conducting_id] = history.result.person_conducting 
        if lResultsPosition > 0 and lResultsPosition < 9000:
            lTotalPositions += lResultsPosition
            lResultsWithPositionCount += 1
            if lResultsPosition == 1:
                lWinsCount += 1
            elif lResultsPosition <= 6:
                lTopSixNotWinCount += 1
            else:
                lUnplacedCount += 1
        else:
            lUnplacedCount += 1
            
    lAveragePosition = 0
    if lResultsWithPositionCount > 0:
        lAveragePosition = lTotalPositions / lResultsWithPositionCount   
        
    lPlayerPositions = PlayerPosition.objects.all()
        
    return render_auth(request, 'users/profile/performances.html', {
                                                            'User' : lUser,
                                                            'Profile' : lProfile,
                                                            'FeedbackCount' : lOutstandingFeedbackCount,
                                                            "ContestCount" : lContestsCount,
                                                            'SentFeedbackCount' : lSentFeedbackCount,
                                                            'PerformanceCount' : lContestHistoryCount, 
                                                            "ContestHistory" : lContestHistory,
                                                            "DateRanges" : lUserDateRanges,
                                                            "ImportedCount" : lCount,
                                                            "ContestHistoryVisibility" : lProfile.contest_history_visibility,
                                                            "ResultsWithPosition": lResultsWithPositionCount,
                                                            "Wins": lWinsCount,
                                                            "TopSixNotWin":lTopSixNotWinCount,
                                                            "Unplaced": lUnplacedCount,
                                                            "BandCount" : len(lHistoryBands),
                                                            "ConductorCount": len(lHistoryConductors),
                                                            "HistoryBands" : lHistoryBands.values(),
                                                            "HistoryConductors" : lHistoryConductors.values(),
                                                            "MessageCount" : lMessageCount,
                                                            "UserBadges" : lUserBadges,
                                                            "AveragePosition": lAveragePosition,
                                                            "Positions" : lPlayerPositions,
                                                            })      
    
@login_required
def messages(request, pUsername):
    """
    Show messages
    """
    try:
        lUser = User.objects.filter(username=pUsername)[0]
    except IndexError:
        raise Http404
    lProfile = lUser.profile
    
    if pUsername != lUser.username:
        raise Http404
    
    lOutstandingFeedbackCount, lSentFeedbackCount, lContestsCount, lContestHistoryCount, lMessageCount, lUserBadges = _get_tab_counts(request, lUser)
        
    lMessages = Message.objects.filter(to_user=request.user).filter(deleted=False)
        
    return render_auth(request, 'users/profile/messages.html', {
                                                            'User' : lUser,
                                                            'Profile' : lProfile,
                                                            "ContestCount" : lContestsCount,
                                                            'FeedbackCount' : lOutstandingFeedbackCount,
                                                            'SentFeedbackCount' : lSentFeedbackCount,
                                                            'PerformanceCount' : lContestHistoryCount, 
                                                            "MessageCount" : lMessageCount,
                                                            "Messages" : lMessages,
                                                            "UserBadges" : lUserBadges,
                                                            })    
    
@login_required
def classifieds(request, pUsername):
    """
    Show classified profiles
    """
    try:
        lUser = User.objects.filter(username=pUsername)[0]
    except IndexError:
        raise Http404
    lProfile = lUser.profile
    
    if pUsername != lUser.username:
        raise Http404
    
    lOutstandingFeedbackCount, lSentFeedbackCount, lContestsCount, lContestHistoryCount, lMessageCount, lUserBadges = _get_tab_counts(request, lUser)
    
    lClassifiedProfiles = ClassifiedPerson.objects.filter(owner=request.user)
        
    return render_auth(request, 'users/profile/classifieds.html', {
                                                            'User' : lUser,
                                                            'Profile' : lProfile,
                                                            "ContestCount" : lContestsCount,
                                                            'FeedbackCount' : lOutstandingFeedbackCount,
                                                            'SentFeedbackCount' : lSentFeedbackCount,
                                                            'PerformanceCount' : lContestHistoryCount, 
                                                            "MessageCount" : lMessageCount,
                                                            "ClassifiedProfiles" : lClassifiedProfiles,
                                                            "UserBadges" : lUserBadges,
                                                            })        
@login_required
def notifications(request, pUsername):
    """
    Show notifications page in user profile
    """ 
    if request.user.is_superuser == False:
        raise Http404
       
    try:
        lUser = User.objects.filter(username=pUsername)[0]
    except IndexError:
        raise Http404
    lProfile = lUser.profile
    
    if pUsername != lUser.username:
        raise Http404
    
    lOutstandingFeedbackCount, lSentFeedbackCount, lContestsCount, lContestHistoryCount, lMessageCount, lUserBadges = _get_tab_counts(request, lUser)
    
    return render_auth(request, 'users/profile/notifications.html', {
                                                            'User' : lUser,
                                                            'Profile' : lProfile,
                                                            "ContestCount" : lContestsCount,
                                                            'FeedbackCount' : lOutstandingFeedbackCount,
                                                            'SentFeedbackCount' : lSentFeedbackCount,
                                                            'PerformanceCount' : lContestHistoryCount, 
                                                            "MessageCount" : lMessageCount,
                                                            "UserBadges" : lUserBadges,
                                                             })
    

@csrf_protect
@login_required
def password_change(request, pUsername):
    """
    Show change password form
    """
    if request.method == "POST":
        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            notification(None, request.user, 'users', 'password', 'changed', request.user, browser_details(request), pDestination=request.user.email)
            return HttpResponseRedirect('/users/%s/password_changed/' % pUsername)
        
    else:
        form = PasswordChangeForm(user=request.user)
    
    return render_auth(request, 'users/changepassword.html', {'form' : form})


def password_change_done(request, pUsername):
    """
    Password change has been done
    """
    try:
        lUser = User.objects.filter(username=pUsername)[0]
    except IndexError:
        raise Http404
    
    return render_auth(request, 'users/changepassword_done.html', {'User' : lUser})

@login_required
def new_email_required(request, pUsername):
    """
    Email has been marked as invalid, need to enter a new one
    """
    if request.method == "POST":
        form = NewEmailForm(data=request.POST)
        if form.is_valid():
            request.user.email = form.cleaned_data['email']
            request.user.save()
            return HttpResponseRedirect('/')
        
    else:
        form = NewEmailForm()
    return render_auth(request, 'users/new_email_required.html', {'form' : form})


@login_required
def talk(request, pUsername):
    """
    Show the talk page for a particular user
    """
    if request.user.profile.superuser == False:
        raise Http404
    
    try:
        lTalkUser = User.objects.filter(username=pUsername)[0]
    except IndexError:
        raise Http404
    
    try:
        lTalk = UserTalk.objects.filter(owner=lTalkUser)[0]
    except IndexError:
        lTalk = None
        
    lEditEnabled = False
    if lTalkUser.username == request.user.username:
        lEditEnabled = True
        
    lSuperusers = UserProfile.objects.filter(superuser=True)
    lRecentTalkChanges = fetch_recent_talk_changes(request)   
    
    return render_auth(request, 'users/talk.html', {
                                                    'TalkUser' : lTalkUser,
                                                    'Talk' : lTalk,
                                                    'EditEnabled' : lEditEnabled,
                                                    'OwnerId' : lTalkUser.id,
                                                    'Superusers' : lSuperusers,
                                                    'RecentTalkChanges' : lRecentTalkChanges,
                                                    })
    
@login_required
def talk_edit(request, pUsername):
    """
    Edit the talk page
    """
    if request.user.profile.superuser == False:
        raise Http404
    
    if request.user.username != pUsername:
        raise Http404
    
    try:
        lTalk = UserTalk.objects.filter(owner=request.user)[0]
    except IndexError:
        lTalk = UserTalk()
        lTalk.owner = request.user
        lTalk.save()
        
    if request.method == "POST":
        form = UserTalkEditForm(data=request.POST, instance=lTalk)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/users/%s/talk/' % request.user.username)
        
    else:
        form = UserTalkEditForm(instance=lTalk)        
        
    return render_auth(request, 'users/talk_edit.html', {
                                                    'Talk' : lTalk,
                                                    'form' : form,
                                                    })


@login_required
def pro_upgrade(request):
    """
    Upgrade to a pro account
    """
    lStripePublicCode = settings.STRIPE_PUBLIC_DATA_KEY
    return render_auth(request, 'users/pro/upgrade.html', {'StripePublicCode' : lStripePublicCode})


@login_required
def pro_paid(request):
    """
    Paid, activate pro account
    """
    lCurrentUserProfile = request.user.profile
    lCurrentUserProfile.pro_member = True;
    lCurrentUserProfile.stripe_token = request.POST.get('stripeToken')
    lCurrentUserProfile.stripe_email = request.POST.get('stripeEmail')
    lCurrentUserProfile.save()
    
    import stripe
    stripe.api_key = settings.STRIPE_SECRET_KEY
    
    try:
        # Use Stripe's bindings...
        lCustomer = stripe.Customer.create(description=request.user.username,
                                           source=lCurrentUserProfile.stripe_token,
                                           email=lCurrentUserProfile.stripe_email)
        lCustomer.subscriptions.create(plan='BBRPRO')  
        
        lCurrentUserProfile.stripe_customer = lCustomer.id
        lCurrentUserProfile.save()
    except stripe.error.CardError as e:
        # Since it's a decline, stripe.error.CardError will be caught
        body = e.json_body
        err  = body['error']
    except stripe.error.InvalidRequestError as e:
        # Invalid parameters were supplied to Stripe's API
        pass
    except stripe.error.AuthenticationError as e:
        # Authentication with Stripe's API failed
        # (maybe you changed API keys recently)
        pass
    except stripe.error.APIConnectionError as e:
        # Network communication with Stripe failed
        pass
    except stripe.error.StripeError as e:
        # Display a very generic error to the user, and maybe send
        # yourself an email
        pass
    except Exception as e:
        # Something else happened, completely unrelated to Stripe
        pass
    
    
    notification(request.user, None, 'users', 'pro_upgrade', 'paid', request.user, browser_details(request))
    
    return HttpResponseRedirect('/accounts/pro/thanks/')



@login_required
def pro_thanks(request):
    """
    Thanks for upgrading to pro
    """
    return render_auth(request, 'users/pro/activated.html', {})