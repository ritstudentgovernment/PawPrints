"""
filename: social_tags.py
description: Custom tag for importing social items to any Django app.
author:	Omar De La Hoz (omardlhz)
created on: Nov 30 2016
updated on: Dec 02 2016
"""
from django import template
from django.template.loader import get_template
from django.core.urlresolvers import resolve
from django.http import HttpRequest
from django.contrib.sites.shortcuts import get_current_site

register = template.Library()

#	Usage:
#	
#	{% load social_tags %}				//	Load the custom tag.
#	{{ petition_url|social_widget }}	//  Place where desired (Recommendation: enclose within a div)
#										//  The size of the widget adopts the size of its container.
@register.filter(name='social_widget')
def social_widget(petition_url):
	return get_template('social-widget.html').render(template.Context({'petition_url': petition_url}));


#   Usage:
#
#   {% load social_tags %}				//	Load the custom tag.
#   {{ petition_url|social_bar }}       //  Place in the templates head.
#                                       //  The size of this side-bar is fixed (edit in template if desired)
@register.filter(name='social_bar')
def social_bar(petition_url):
    return get_template('social-bar.html').render(template.Context({'petition_url': petition_url}));
