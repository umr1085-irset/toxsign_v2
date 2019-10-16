from django import template

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
