# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved

from django.urls import re_path

from . import views

urlpatterns = [
    re_path(r'^$', views.user_list),
    re_path(r'^([@_\.\+\-\w]+)/$', views.user_profile),
    re_path(r'^([@_\.\+\-\w]+)/change_password/$', views.password_change),
    re_path(r'^([@_\.\+\-\w]+)/password_changed/$', views.password_change_done),
    re_path(r'^([@_\.\+\-\w]+)/new_email_required/$', views.new_email_required),
    re_path(r'^([@_\.\+\-\w]+)/talk/$', views.talk),
    re_path(r'^([@_\.\+\-\w]+)/talk/edit/$', views.talk_edit),
    re_path(r'^([@_\.\+\-\w]+)/year/(\d+)/$', views.user_contests_year),
    
    re_path(r'^([@_\.\+\-\w]+)/contesthistory/$', views.maintain_date_ranges),
    re_path(r'^([@_\.\+\-\w]+)/contesthistory/(\d+)/delete/$', views.delete_date_range),
    re_path(r'^([@_\.\+\-\w]+)/contesthistory/(\d+)/import/$', views.import_contests_date_range),
    re_path(r'^([@_\.\+\-\w]+)/contesthistory/(\d+)/remove_contest/$', views.remove_contest_from_list),
    re_path(r'^([@_\.\+\-\w]+)/contesthistory/(\d+)/approve_contest/$', views.approve_contest_in_list),
    re_path(r'^([@_\.\+\-\w]+)/contesthistory/(\d+)/set_position/(\d+)/$', views.set_instrument_in_list),
    
    re_path(r'^([@_\.\+\-\w]+)/queue/(\d+)/$', views.feedback_release_to_queue),
    re_path(r'^([@_\.\+\-\w]+)/inconclusive/(\d+)/$', views.feedback_inconclusive),
    re_path(r'^([@_\.\+\-\w]+)/claim/(\d+)/$', views.feedback_claim_from_queue),
    re_path(r'^([@_\.\+\-\w]+)/admin/(\d+)/$', views.feedback_push_to_admin),
    re_path(r'^([@_\.\+\-\w]+)/feedbacknotdone/(\d+)/$', views.feedback_not_done),
    re_path(r'^([@_\.\+\-\w]+)/feedbackdone/(\d+)/$', views.feedback_done),
    
    re_path(r'^([@_\.\+\-\w]+)/edit_profile/(\d+)/$', views.edit_profile),
    re_path(r'^([@_\.\+\-\w]+)/edit_band_profile/(\d+)/$', views.edit_band_profile),
    
    re_path(r'^([@_\.\+\-\w]+)/feedback_sent/$', views.feedback_sent),
    re_path(r'^([@_\.\+\-\w]+)/results_added/$', views.results_added),
    re_path(r'^([@_\.\+\-\w]+)/contest_history/$', views.contest_history),
    re_path(r'^([@_\.\+\-\w]+)/messages/$', views.messages),
    re_path(r'^([@_\.\+\-\w]+)/classifieds/$', views.classifieds),
    re_path(r'^([@_\.\+\-\w]+)/notifications/$', views.notifications),    
]



