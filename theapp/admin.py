"""
The admin interface for the application.
"""

from django.contrib import admin

from theapp.models import MODELS_LIST


def generate_admins():
	"""
	Generage the admin classes from models.
	"""
	for model_cls in MODELS_LIST:
		admin_cls = type(model_cls.__name__ + "Admin", (admin.ModelAdmin,), {
			"list_display": [x.name for x in model_cls._meta.fields
				if x.name != "id"]
			})
		admin.site.register(model_cls, admin_cls)

generate_admins()
