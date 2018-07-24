# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved

from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.user_list),
    url(r'^([@_\.\+\-\w]+)/$', views.user_profile),
    url(r'^([@_\.\+\-\w]+)/change_password/$', views.password_change),
    url(r'^([@_\.\+\-\w]+)/password_changed/$', views.password_change_done),
    url(r'^([@_\.\+\-\w]+)/new_email_required/$', views.new_email_required),
    url(r'^([@_\.\+\-\w]+)/talk/$', views.talk),
    url(r'^([@_\.\+\-\w]+)/talk/edit/$', views.talk_edit),
    url(r'^([@_\.\+\-\w]+)/year/(\d+)/$', views.user_contests_year),
    
    url(r'^([@_\.\+\-\w]+)/contesthistory/$', views.maintain_date_ranges),
    url(r'^([@_\.\+\-\w]+)/contesthistory/(\d+)/delete/$', views.delete_date_range),
    url(r'^([@_\.\+\-\w]+)/contesthistory/(\d+)/import/$', views.import_contests_date_range),
    url(r'^([@_\.\+\-\w]+)/contesthistory/(\d+)/remove_contest/$', views.remove_contest_from_list),
    url(r'^([@_\.\+\-\w]+)/contesthistory/(\d+)/approve_contest/$', views.approve_contest_in_list),
    url(r'^([@_\.\+\-\w]+)/contesthistory/(\d+)/set_position/(\d+)/$', views.set_instrument_in_list),
    
    url(r'^([@_\.\+\-\w]+)/queue/(\d+)/$', views.feedback_release_to_queue),
    url(r'^([@_\.\+\-\w]+)/inconclusive/(\d+)/$', views.feedback_inconclusive),
    url(r'^([@_\.\+\-\w]+)/claim/(\d+)/$', views.feedback_claim_from_queue),
    url(r'^([@_\.\+\-\w]+)/admin/(\d+)/$', views.feedback_push_to_admin),
    url(r'^([@_\.\+\-\w]+)/feedbacknotdone/(\d+)/$', views.feedback_not_done),
    url(r'^([@_\.\+\-\w]+)/feedbackdone/(\d+)/$', views.feedback_done),
    
    url(r'^([@_\.\+\-\w]+)/edit_profile/(\d+)/$', views.edit_profile),
    url(r'^([@_\.\+\-\w]+)/edit_band_profile/(\d+)/$', views.edit_band_profile),
    
    url(r'^([@_\.\+\-\w]+)/feedback_sent/$', views.feedback_sent),
    url(r'^([@_\.\+\-\w]+)/results_added/$', views.results_added),
    url(r'^([@_\.\+\-\w]+)/contest_history/$', views.contest_history),
    url(r'^([@_\.\+\-\w]+)/messages/$', views.messages),
    url(r'^([@_\.\+\-\w]+)/classifieds/$', views.classifieds),
    url(r'^([@_\.\+\-\w]+)/notifications/$', views.notifications),    
]



