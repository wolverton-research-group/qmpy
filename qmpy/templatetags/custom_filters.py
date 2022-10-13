from django import template
import os

register = template.Library()


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def USE_CDN(_):
    return True if os.environ.get("OQMD_USE_CDN").lower() == "true" else False


@register.filter
def IS_DEBUG(_):
    return True if os.environ.get("OQMD_WEB_debug").lower() == "true" else False
