"""
The form functions for the application.
"""

from django.forms import ModelForm


def get_model_form(model_cls, model_field=None):
	"""
	Get ModelForm for the model class.
	"""
	name = model_cls.__name__ + "Form"
	fields = (model_field,)
	if model_field is None:
		fields = tuple(model_cls._meta.get_all_field_names())
	else:
		name += model_field

	return type(str(name), (ModelForm, ), {
		"Meta": type("Meta", (), {
			"model": model_cls,
			"fields": fields
			})
		})
