DROP TABLE celery_taskmeta;
DROP TABLE celery_tasksetmeta;

DROP TABLE djcelery_crontabschedule CASCADE;
DROP TABLE djcelery_intervalschedule CASCADE;
DROP TABLE djcelery_periodictask;
DROP TABLE djcelery_periodictasks;
DROP TABLE djcelery_taskstate;
DROP TABLE djcelery_workerstate;

DROP TABLE census_censusentry;

DROP TABLE dj_banner_banner CASCADE;
DROP TABLE dj_banner_bannermonthcounter;
DROP TABLE dj_banner_bannerset CASCADE;
DROP TABLE dj_banner_bannerweight;
DROP TABLE dj_banner_contract CASCADE;
DROP TABLE dj_banner_month;

DROP TABLE paypal_discountcode;
DROP TABLE paypal_ipnlog;
DROP TABLE paypal_paypalpaymentcode;

DROP TABLE rankings_availablepoints;
DROP TABLE rankings_bankrankingsetup;
DROP TABLE rankings_pointscalculation;
DROP TABLE rankings_pointsdecay;
DROP TABLE rankings_resultscache;
DROP TABLE rankings_seedpointscalculation;
DROP TABLE rankings_seedpointsmultiplier;

DELETE FROM django_session;

GRANT ALL PRIVILEGES ON DATABASE bbr TO bbr;

#SELECT exec('GRANT ALL ON ' || table_schema || '.' || table_name || ' TO bbr;')
#FROM information_schema.tables
#WHERE table_schema = 'public'

 GRANT ALL ON public.geography_columns TO bbr;
 GRANT ALL ON public.raster_overviews TO bbr;
 GRANT ALL ON public.geometry_columns TO bbr;
 GRANT ALL ON public.raster_columns TO bbr;
 GRANT ALL ON public.spatial_ref_sys TO bbr;
 GRANT ALL ON public.auth_group TO bbr;
 GRANT ALL ON public.auth_user TO bbr;
 GRANT ALL ON public.auth_permission TO bbr;
 GRANT ALL ON public.badges_badge TO bbr;
 GRANT ALL ON public.auth_message TO bbr;
 GRANT ALL ON public.auth_user_groups TO bbr;
 GRANT ALL ON public.auth_user_user_permissions TO bbr;
 GRANT ALL ON public.bands_bandrelationship TO bbr;
 GRANT ALL ON public.bandnews_feed TO bbr;
 GRANT ALL ON public.bands_previousbandname TO bbr;
 GRANT ALL ON public.bands_bandtalkpage TO bbr;
 GRANT ALL ON public.classifieds_playerposition TO bbr;
 GRANT ALL ON public.contests_contestachievementaward TO bbr;
 GRANT ALL ON public.bandnews_newsitem TO bbr;
 GRANT ALL ON public.contests_contest TO bbr;
 GRANT ALL ON public.contests_contestprogrammepage TO bbr;
 GRANT ALL ON public.contests_contestweblink TO bbr;
 GRANT ALL ON public.contests_contesttalkpage TO bbr;
 GRANT ALL ON public.contests_contesttype TO bbr;
 GRANT ALL ON public.contests_contestgroupalias TO bbr;
 GRANT ALL ON public.contests_currentchampion TO bbr;
 GRANT ALL ON public.contests_contestresult TO bbr;
 GRANT ALL ON public.contests_contesteventweblink TO bbr;
 GRANT ALL ON public.contests_contestgrouplinkeventlink TO bbr;
 GRANT ALL ON public.contests_contesttestpiece TO bbr;
 GRANT ALL ON public.contests_contestgroup TO bbr;
 GRANT ALL ON public.django_admin_log TO bbr;
 GRANT ALL ON public.django_content_type TO bbr;
 GRANT ALL ON public.django_migrations TO bbr;
 GRANT ALL ON public.django_session TO bbr;
 GRANT ALL ON public.contests_resultpieceperformance TO bbr;
 GRANT ALL ON public.contests_grouptalkpage TO bbr;
 GRANT ALL ON public.django_site TO bbr;
 GRANT ALL ON public.contests_venue TO bbr;
 GRANT ALL ON public.feedback_clarificationrequest TO bbr;
 GRANT ALL ON public.feedback_sitefeedback TO bbr;
 GRANT ALL ON public.move_venuemergerequest TO bbr;
 GRANT ALL ON public.move_bandmergerequest TO bbr;
 GRANT ALL ON public.move_personmergerequest TO bbr;
 GRANT ALL ON public.move_piecemergerequest TO bbr;
 GRANT ALL ON public.news_newspublisher TO bbr;
 GRANT ALL ON public.messages_message TO bbr;
 GRANT ALL ON public.home_faqsection TO bbr;
 GRANT ALL ON public.people_classifiedperson TO bbr;
 GRANT ALL ON public.pieces_downloadstore TO bbr;
 GRANT ALL ON public.news_sentpublishermessage TO bbr;
 GRANT ALL ON public.pieces_testpiece TO bbr;
 GRANT ALL ON public.paypal_paypalpaymentcode TO bbr;
 GRANT ALL ON public.payments_userpayment TO bbr;
 GRANT ALL ON public.news_newssite TO bbr;
 GRANT ALL ON public.rankings_availablepoints TO bbr;
 GRANT ALL ON public.people_personalias TO bbr;
 GRANT ALL ON public.paypal_discountcode TO bbr;
 GRANT ALL ON public.people_personrelation TO bbr;
 GRANT ALL ON public.pieces_testpiecealias TO bbr;
 GRANT ALL ON public.rankings_resultscache TO bbr;
 GRANT ALL ON public.rankings_pointscalculation TO bbr;
 GRANT ALL ON public.rankings_pointsdecay TO bbr;
 GRANT ALL ON public.south_migrationhistory TO bbr;
 GRANT ALL ON public.thumbnail_kvstore TO bbr;
 GRANT ALL ON public.users_passwordreset TO bbr;
 GRANT ALL ON public.rankings_seedpointscalculation TO bbr;
 GRANT ALL ON public.users_pointsaward TO bbr;
 GRANT ALL ON public.sections_section TO bbr;
 GRANT ALL ON public.regions_region TO bbr;
 GRANT ALL ON public.users_usertalk TO bbr;
 GRANT ALL ON public.users_useripaddress TO bbr;
 GRANT ALL ON public.users_userbadge TO bbr;
 GRANT ALL ON public.users_userprofile_regional_superuser_regions TO bbr;
 GRANT ALL ON public.venues_venuealias TO bbr;
 GRANT ALL ON public.embed_embeddedresultslog TO bbr;
 GRANT ALL ON public.audit_auditentry TO bbr;
 GRANT ALL ON public.news_bandpublisher TO bbr;
 GRANT ALL ON public.users_userprofile TO bbr;
 GRANT ALL ON public.auth_group_permissions TO bbr;
 GRANT ALL ON public.news_newsitem TO bbr;
 GRANT ALL ON public.people_person TO bbr;
 GRANT ALL ON public.contests_contestprogrammecover TO bbr;
 GRANT ALL ON public.pieces_downloadtrack TO bbr;
 GRANT ALL ON public.tags_contesttag TO bbr;
 GRANT ALL ON public.contests_contestevent TO bbr;
 GRANT ALL ON public.contests_contestalias TO bbr;
 GRANT ALL ON public.adjudicators_contestadjudicator TO bbr;
 GRANT ALL ON public.pieces_downloadalbum TO bbr;
 GRANT ALL ON public.rankings_bandrankingssetup TO bbr;
 GRANT ALL ON public.contests_contestgroup_tags TO bbr;
 GRANT ALL ON public.users_personalcontesthistorydaterange TO bbr;
 GRANT ALL ON public.bands_bandgrading TO bbr;
 GRANT ALL ON public.users_usernotification TO bbr;
 GRANT ALL ON public.contests_contestgroupweblink TO bbr;
 GRANT ALL ON public.paypal_ipnlog TO bbr;
 GRANT ALL ON public.rankings_seedpointsmultiplier TO bbr;
 GRANT ALL ON public.registration_registrationprofile TO bbr;
 GRANT ALL ON public.users_personalcontesthistory TO bbr;
 GRANT ALL ON public.contests_contest_tags TO bbr;
 GRANT ALL ON public.home_faqentry TO bbr;
 GRANT ALL ON public.bands_band TO bbr;

#SELECT exec('GRANT ALL ON ' || relname || ' TO bbr;')
#FROM pg_class
#WHERE relkind = 'S'
#AND relowner > 10

 GRANT ALL ON auth_message_id_seq TO bbr;
 GRANT ALL ON auth_permission_id_seq TO bbr;
 GRANT ALL ON adjudicators_contestadjudicator_id_seq TO bbr;
 GRANT ALL ON audit_auditentry_id_seq TO bbr;
 GRANT ALL ON auth_group_id_seq TO bbr;
 GRANT ALL ON auth_group_permissions_id_seq TO bbr;
 GRANT ALL ON auth_user_groups_id_seq TO bbr;
 GRANT ALL ON auth_user_id_seq TO bbr;
 GRANT ALL ON auth_user_user_permissions_id_seq TO bbr;
 GRANT ALL ON badges_badge_id_seq TO bbr;
 GRANT ALL ON bandnews_feed_id_seq TO bbr;
 GRANT ALL ON bandnews_newsitem_id_seq TO bbr;
 GRANT ALL ON bands_band_id_seq TO bbr;
 GRANT ALL ON bands_bandgrading_id_seq TO bbr;
 GRANT ALL ON bands_bandrelationship_id_seq TO bbr;
 GRANT ALL ON bands_bandtalkpage_id_seq TO bbr;
 GRANT ALL ON bands_previousbandname_id_seq TO bbr;
 GRANT ALL ON classifieds_playerposition_id_seq TO bbr;
 GRANT ALL ON contests_contest_id_seq TO bbr;
 GRANT ALL ON contests_contest_tags_id_seq TO bbr;
 GRANT ALL ON contests_contestachievementaward_id_seq TO bbr;
 GRANT ALL ON contests_contestalias_id_seq TO bbr;
 GRANT ALL ON contests_contestevent_id_seq TO bbr;
 GRANT ALL ON contests_contesteventweblink_id_seq TO bbr;
 GRANT ALL ON contests_contestgroup_id_seq TO bbr;
 GRANT ALL ON contests_contestgroup_tags_id_seq TO bbr;
 GRANT ALL ON contests_contestgroupalias_id_seq TO bbr;
 GRANT ALL ON contests_contestgrouplinkeventlink_id_seq TO bbr;
 GRANT ALL ON contests_contestgroupweblink_id_seq TO bbr;
 GRANT ALL ON contests_contestprogrammecover_id_seq TO bbr;
 GRANT ALL ON contests_contestprogrammepage_id_seq TO bbr;
 GRANT ALL ON contests_contesttalkpage_id_seq TO bbr;
 GRANT ALL ON contests_contesttestpiece_id_seq TO bbr;
 GRANT ALL ON contests_contesttype_id_seq TO bbr;
 GRANT ALL ON contests_currentchampion_id_seq TO bbr;
 GRANT ALL ON contests_grouptalkpage_id_seq TO bbr;
 GRANT ALL ON contests_resultpieceperformance_id_seq TO bbr;
 GRANT ALL ON contests_venue_id_seq TO bbr;
 GRANT ALL ON django_migrations_id_seq TO bbr;
 GRANT ALL ON django_admin_log_id_seq TO bbr;
 GRANT ALL ON django_content_type_id_seq TO bbr;
 GRANT ALL ON django_site_id_seq TO bbr;
 GRANT ALL ON embed_embeddedresultslog_id_seq TO bbr;
 GRANT ALL ON feedback_clarificationrequest_id_seq TO bbr;
 GRANT ALL ON feedback_sitefeedback_id_seq TO bbr;
 GRANT ALL ON home_faqentry_id_seq TO bbr;
 GRANT ALL ON home_faqsection_id_seq TO bbr;
 GRANT ALL ON messages_message_id_seq TO bbr;
 GRANT ALL ON move_bandmergerequest_id_seq TO bbr;
 GRANT ALL ON move_personmergerequest_id_seq TO bbr;
 GRANT ALL ON move_piecemergerequest_id_seq TO bbr;
 GRANT ALL ON move_venuemergerequest_id_seq TO bbr;
 GRANT ALL ON news_bandpublisher_id_seq TO bbr;
 GRANT ALL ON news_newsitem_id_seq TO bbr;
 GRANT ALL ON news_newspublisher_id_seq TO bbr;
 GRANT ALL ON news_newssite_id_seq TO bbr;
 GRANT ALL ON news_sentpublishermessage_id_seq TO bbr;
 GRANT ALL ON paypal_discountcode_id_seq TO bbr;
 GRANT ALL ON paypal_ipnlog_id_seq TO bbr;
 GRANT ALL ON paypal_paypalpaymentcode_id_seq TO bbr;
 GRANT ALL ON people_person_id_seq TO bbr;
 GRANT ALL ON people_personalias_id_seq TO bbr;
 GRANT ALL ON people_personrelation_id_seq TO bbr;
 GRANT ALL ON pieces_downloadalbum_id_seq TO bbr;
 GRANT ALL ON pieces_downloadtrack_id_seq TO bbr;
 GRANT ALL ON pieces_testpiece_id_seq TO bbr;
 GRANT ALL ON pieces_testpiecealias_id_seq TO bbr;
 GRANT ALL ON rankings_availablepoints_id_seq TO bbr;
 GRANT ALL ON rankings_bandrankingssetup_id_seq TO bbr;
 GRANT ALL ON rankings_pointscalculation_id_seq TO bbr;
 GRANT ALL ON rankings_pointsdecay_id_seq TO bbr;
 GRANT ALL ON rankings_resultscache_id_seq TO bbr;
 GRANT ALL ON rankings_seedpointscalculation_id_seq TO bbr;
 GRANT ALL ON rankings_seedpointsmultiplier_id_seq TO bbr;
 GRANT ALL ON regions_region_id_seq TO bbr;
 GRANT ALL ON registration_registrationprofile_id_seq TO bbr;
 GRANT ALL ON sections_section_id_seq TO bbr;
 GRANT ALL ON south_migrationhistory_id_seq TO bbr;
 GRANT ALL ON tags_contesttag_id_seq TO bbr;
 GRANT ALL ON users_passwordreset_id_seq TO bbr;
 GRANT ALL ON users_personalcontesthistory_id_seq TO bbr;
 GRANT ALL ON users_personalcontesthistorydaterange_id_seq TO bbr;
 GRANT ALL ON users_pointsaward_id_seq TO bbr;
 GRANT ALL ON users_userbadge_id_seq TO bbr;
 GRANT ALL ON users_useripaddress_id_seq TO bbr;
 GRANT ALL ON users_usernotification_id_seq TO bbr;
 GRANT ALL ON users_userprofile_id_seq TO bbr;
 GRANT ALL ON users_userprofile_regional_superuser_regions_id_seq TO bbr;
 GRANT ALL ON users_usertalk_id_seq TO bbr;
 GRANT ALL ON venues_venuealias_id_seq TO bbr;

UPDATE users_usernotification SET type = 'classifieds.profile.edit' WHERE type = 'edit_profile';
UPDATE users_usernotification SET type = 'contests.contestevent.results_added' WHERE type = 'results_added_contestevent';
UPDATE users_usernotification SET type = 'bands.band.new' WHERE type = 'monthly_new_band';
UPDATE users_usernotification SET type = 'feedback.feedback.new' WHERE type = 'new_feedback';
UPDATE users_usernotification SET type = 'classifieds.profile.new' WHERE type = 'new_profile';
UPDATE users_usernotification SET type = 'classifieds.profile.add' WHERE type = 'add_profile';
UPDATE users_usernotification SET type = 'contests.contestevent.edit' WHERE type = 'edit_contest_event';
UPDATE users_usernotification SET type = 'contests.contest.edit' WHERE type = 'edit_contest';
UPDATE users_usernotification SET type = 'users.reputation.enhanced' WHERE type = 'enhanced_reputation';
UPDATE users_usernotification SET type = 'feedback.feedback.to_admin' WHERE type = 'to_admin_feedback';
UPDATE users_usernotification SET type = 'feedback.feedback.to_admin' WHERE type = 'new_person';
UPDATE users_usernotification SET type = 'feedback.feedback.to_admin' WHERE type = 'new_programme_cover';


