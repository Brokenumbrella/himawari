# -*- coding: utf-8 -*-

"""
Definition custom filter
"""
from django import template

register = template.Library()

@register.filter
def cut_text(value,args):

    from django.utils.safestring import SafeText

    newtext = value
    length = int(args)
    if length > 3:
        if len(newtext) > length:
            newtext = SafeText(newtext)[:(length-3)]
            newtext += '...'
    else:
        newtext = ''
        for n in range(length):
            newtext += '.'
    return newtext
