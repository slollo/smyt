"""
The views for the application.
"""

import jsonpickle
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.utils.translation import ugettext as _

from theapp.models import MODELS_LIST
from theapp.forms import get_model_form


def index(request):
	"""
	Show main page of the application.
	"""
	if not MODELS_LIST:
		raise Http404

	models = {}
	for m in MODELS_LIST:
		models[m.__name__] = {
				"name": m._meta.verbose_name,
				"name_plural": m._meta.verbose_name_plural,
				"fields": [],
			}
		for f in m._meta.fields:
			models[m.__name__]["fields"].append({
					"id": f.name,
					"name": f.verbose_name,
					"type": f.__class__.__name__,
					"max_length": getattr(f, "max_length", None),
					})

	return render_to_response("theapp/index.html", dictionary={
		"models": models
		}, context_instance=RequestContext(request))


def get_content(request):
	"""
	Get a model content from db.
	"""
	model_name = request.GET.get("name", None)
	if model_name is None:
		raise Http404

	model_cls = find_model_cls(model_name)

	if model_cls is None:
		raise Http404

	fields = model_cls._meta.get_all_field_names()
	result = []
	for obj in model_cls.objects.all():
		row = {}
		for field in fields:
			row[field] = getattr(obj, field)

		result.append(row)

	return HttpResponse(jsonpickle.encode(result, unpicklable=False))


def set_field(request):
	"""
	Save field of an object.
	"""
	if request.method == 'POST':
		model_name = request.POST.get("model-name", None)
		field_name = request.POST.get("field-name", None)
		model_cls = find_model_cls(model_name)
		if field_name in [None, "id"] or model_cls is None:
			raise Http404

		if field_name not in model_cls._meta.get_all_field_names():
			raise Http404

		pk = request.POST.get("id")
		if pk is None:
			raise Http404

		instance = get_object_or_404(model_cls, id=pk)

		form_cls = get_model_form(model_cls, field_name)
		form = form_cls(request.POST, instance=instance)

		if form.is_valid():
			form.save()
			return HttpResponse()

		return HttpResponse("\n".join(form.errors[field_name]))

	return HttpResponse(_("Only POST request allowed"))


def create(request):
	"""
	Create new object for a model.
	"""
	if request.method == 'POST':
		model_name = request.POST.get("model-name", None)
		model_cls = find_model_cls(model_name)
		if model_cls is None:
			raise Http404

		form_cls = get_model_form(model_cls)
		form = form_cls(request.POST)

		if form.is_valid():
			form.save()
			return HttpResponse()

		return HttpResponse("\n".join(
			["{0}: {1}".format(k, v.as_text()) for k, v in form.errors.items()]))

	return HttpResponse(_("Only POST request allowed"))


def find_model_cls(name):
	"""
	Find model class by name.
	"""
	for m in MODELS_LIST:
		if m.__name__ == name:
			return m

	return None



