from django.utils.safestring import mark_safe
from django.conf import settings

def thumbnail(pathToImage, dimensions):
    lExtension = pathToImage[pathToImage.rfind('.'):]
    lThumbPath = "%s%s-%s%s" % (settings.THUMB_URL, pathToImage, dimensions, lExtension)
    return mark_safe("<img src='%s'/>" % lThumbPath)

thumbnail.is_safe=True
thumbnail.needs_autoescape = False

register = template.Library()
register.simple_tag(thumbnail)