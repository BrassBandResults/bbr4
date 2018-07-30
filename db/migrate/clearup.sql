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

DELETE FROM django_session;