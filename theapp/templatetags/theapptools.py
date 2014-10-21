
import json as jsonlib
from django import template

register = template.Library()

@register.filter
def json(data):
	"""
	Return json representation of the data.
	"""
	return jsonlib.dumps(data)

