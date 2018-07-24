# -*- coding: utf-8 -*-
# (c) 2009, 2012, 2015 Tim Sawyer, All Rights Reserved

from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter
@stringfilter
def bbrize(value, autoescape=None):
    from django.utils.html import urlize
    import re
    # Link URLs
    value = urlize(value, nofollow=False, autoescape=autoescape)
    # process [type/slug|name] into link to that thing on bbr
    value = re.sub(r'(\s+|\A)\[(\w+)/([\w\d\-/]+)/?\|([^\]]+)\]',r'\1<a href="/\2/\3">\4</a>',value)
    return mark_safe(value)
bbrize.is_safe=True
bbrize.needs_autoescape = True