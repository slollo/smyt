"""
Models generation for the application.
"""

import yaml
from django.db import models

from theapp import settings

FIELD_TYPES = {
		"char": {"type": models.CharField, "attrs": {"max_length": 512}},
		"int":  {"type": models.IntegerField, "attrs": {}},
		"date": {"type": models.DateField, "attrs": {}},
		}

MODELS_LIST = []


def generate_models(yaml_config):
	"""
	Generage the models classes from a yaml config.
	"""

	for model_name, config in yaml_config.items():
		attrs = {'__module__': 'theapp.models'}
		for field in config["fields"]:
			field_type = FIELD_TYPES[field["type"]]["type"]

			field_attrs = FIELD_TYPES[field["type"]]["attrs"]
			for key, val in field.items():
				if key in ["id", "type", "title"]:
					continue
				field_attrs[key] = val

			attrs[field["id"]] = field_type(field["title"], **field_attrs)

		attrs["Meta"] = type("Meta", (), {
					"verbose_name": config["title"],
					"verbose_name_plural":
						config.get("title_plural", config["title"])
					})

		model_cls = type(model_name, (models.Model,), attrs)

		MODELS_LIST.append(model_cls)


def get_yaml(filename):
	"""
	Get content of the yaml config.
	"""
	return yaml.load(file(filename, 'r'))


generate_models(get_yaml(settings.THEAPP_MODELS_YAML_CONFIG))

