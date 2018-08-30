from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='escapejsonquote')
def escape_json_quote(value):
  return mark_safe(value.replace('\\','\\\\'))
