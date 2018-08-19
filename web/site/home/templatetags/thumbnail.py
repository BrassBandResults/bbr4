from django.utils.safestring import mark_safe
from django.conf import settings
from django import template

def thumbnail(imageFieldFile, dimensions):
    lPathToImage = imageFieldFile.url
    lExtension = lPathToImage[lPathToImage.rfind('.'):]
    lThumbPath = "%s/%s-%s%s" % (settings.THUMBS_URL, lPathToImage, dimensions, lExtension)
    return mark_safe("<img src='%s'/>" % lThumbPath)

thumbnail.is_safe=True
thumbnail.needs_autoescape = False

register = template.Library()
register.simple_tag(thumbnail)