from django import template

register = template.Library()

@register.filter(name='escapejsonquote')
def escape_json_quote(value):
  return value.replace('\\"','\\\"')
