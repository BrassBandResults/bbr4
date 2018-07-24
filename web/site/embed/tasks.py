# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved

from celery.task import task

from embed.models import EmbeddedResultsLog

@task(ignore_result=True)
def log_embed_access(pBandSlug, pBand, pBrowserDetails, pReferer):
    """
    Log the fact that the embedded results page has been requested
    """
    lEmbeddedResultsLog = EmbeddedResultsLog()
    lEmbeddedResultsLog.band_slug = pBandSlug
    lEmbeddedResultsLog.band = pBand
    lEmbeddedResultsLog.ip = pBrowserDetails[0]
    if len(pBrowserDetails[0]) == 0:
        lEmbeddedResultsLog.ip = '127.0.0.1'
    lBrowserId = pBrowserDetails[1]
    if len(lBrowserId) > 1020:
        lBrowserId = lBrowserId[0:1020]
    lEmbeddedResultsLog.browser_id = lBrowserId
    lReferer = pReferer
    if len(lReferer) > 250:
        lReferer = lReferer[0:250]
    lEmbeddedResultsLog.referer = lReferer
    lEmbeddedResultsLog.save()