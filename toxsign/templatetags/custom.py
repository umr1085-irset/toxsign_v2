from django import template
from django.utils.html import format_html
from collections.abc import Mapping

register = template.Library()

@register.simple_tag
def onto_value(value, substitute=None):
    data = "None"

    if value:
        data = value

    if substitute and not value:
        data = substitute

    return data

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

@register.simple_tag()
def get_dict_value(dict, value):
    if value in dict:
        return dict[value]
    else:
        return "/"

@register.simple_tag()
def get_model_group_data(dict, group_id, field):
    if group_id in dict:
        return "{:.3f}".format(dict[group_id][field])
    else:
        return "/"

@register.simple_tag()
def get_chemicals(signature):
    chemicals = []
    if signature.factor.chemical_subfactor_of:
        for subfactor in signature.factor.chemical_subfactor_of.all():
            if subfactor.chemical:
                chemicals.append(subfactor.chemical.name)
            elif subfactor.chemical_slug:
                chemicals.append(subfactor.chemical_slug)
    if chemicals:
        res = ", ".join(chemicals).capitalize()
    else:
        res = "/"
    return res

@register.simple_tag()
def get_chemicals_es(signature):
    chemicals = []
    if signature.factor.chemical_subfactor_of:
        for subfactor in signature.factor.chemical_subfactor_of:
            if subfactor.chemical:
                chemicals.append(subfactor.chemical.name)
            elif subfactor.chemical_slug:
                chemicals.append(subfactor.chemical_slug)
    if chemicals:
        res = ", ".join(chemicals).capitalize()
    else:
        res = "/"
    return res

@register.simple_tag(takes_context=True)
def show_username(context, entity):
    username = "/"
    if isinstance(entity, Mapping):
        user = entity['created_by']
    else:
        user = entity.created_by

    if user.is_superuser:
        username = user.username
    elif context["request"].user.is_authenticated:
        username = user.username
    return username


