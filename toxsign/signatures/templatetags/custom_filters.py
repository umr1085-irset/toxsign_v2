from django import template

register = template.Library()

@register.filter
def onto_value(value):
    if value.exists():
        return value
    else:
        return "None"
