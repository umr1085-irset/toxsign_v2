from django import template
from django.utils.html import format_html

register = template.Library()

@register.simple_tag
def onto_value(value, type="foreign", substitute=None):
    # Need to make a distinction between foreign keys and m2m.. not optimal
    if type == "foreign":
        if value:
            return value
    if type == "m2m":
        if value.exists():
            result = []
            for val in value.all():
                result.append(val.name)
            return ", ".join(result)
    if substitute:
        return substitute

    return "None"

@register.simple_tag(takes_context=True)
def url_replace(context, field, value):
    request = context['request']
    dict_ = request.GET.copy()
    if field == 'filter':
        if 'desc' in dict_:
            if dict_['desc'] == value:
                dict_.pop('desc', None)
                dict_['asc'] = value
            else:
                dict_['desc'] = value
                dict_.pop('asc', None)

        elif 'asc' in dict_:
            if dict_['asc'] == value:
                dict_.pop('asc', None)
                dict_['desc'] = value
            else:
                dict_['asc'] = value
                dict_.pop('desc', None)
        else:
            dict_['desc'] = value

    else:
        dict_[field] = value

    return dict_.urlencode()

@register.simple_tag()
def get_arrow(value):
    arrow = ""
    if value == "asc":
        arrow="<i class='fas fa-arrow-up'></i>"
    elif value == "desc":
        arrow="<i class='fas fa-arrow-down'></i>"
    return format_html(arrow)

@register.simple_tag
def get_dict_value(dict, value):
    if value in dict:
        return dict[value]
    else:
        return "/"
