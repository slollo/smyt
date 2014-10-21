# coding: utf-8

import json
from datetime import date, datetime
from django.core.urlresolvers import reverse
from django.test import TestCase
from django.test.client import Client
from django.utils.translation import ugettext as _

from theapp.models import MODELS_LIST

DATA_FIELDS = {
		"CharField": "This form allows you to generate random text strings",
		"IntegerField": 9776456036,
		"DateField": "2014-10-21",
		}

NEWDATA_FIELDS = {
		"CharField": u"А как было бы здорово, если где-нибудь можно было…",
		"IntegerField": 8730217421,
		"DateField": "2013-11-13",
		}

BADDATA_FIELDS = {
		"CharField": ("This form allows you to generate random text strings" * 1000,
			_("Ensure this value has at most %(limit_value)d characters "
			"(it has %(show_value)d).")),
		"IntegerField": ("x9776456036", _("Enter a whole number.")),
		"DateField": ("2014-10-21-281", _("Enter a valid date.")),
		}


class TheappTest(TestCase):
	"""
	Test the application.
	"""
	def setUp(self):
		self.client = Client()

	def test_index(self):
		"""
		Try to get the main page.
		"""
		url = reverse("theapp-index")

		response = self.client.get(url)

		self.assertEquals(response.status_code, 200)
		for m in MODELS_LIST:
			self.assertContains(response, m._meta.verbose_name_plural)

	def test_get_content_badmodel(self):
		"""
		Try to get table content (bad parameters).
		"""
		url = reverse("theapp-get_content")

		response = self.client.get(url)
		self.assertEquals(response.status_code, 404)

		response = self.client.get(url, {"name": "12345"})
		self.assertEquals(response.status_code, 404)

	def create_objects(self):
		"""
		Create model objects.
		"""
		for model_cls in MODELS_LIST:
			data = {}
			for f in model_cls._meta.fields:
				if f.__class__.__name__ in DATA_FIELDS:
					data[f.name] = DATA_FIELDS[f.__class__.__name__]
			model_cls(**data).save()

	def test_get_content(self):
		"""
		Try to get table content via the view.
		"""
		url = reverse("theapp-get_content")

		self.create_objects()

		for model_cls in MODELS_LIST:
			response = self.client.get(url, {"name": model_cls.__name__})
			self.assertEquals(response.status_code, 200)

			for obj in json.loads(response.content):
				for f in model_cls._meta.fields:
					if f.__class__.__name__ in DATA_FIELDS:
						val = DATA_FIELDS[f.__class__.__name__]

						self.assertEqual(obj[f.name], val)

	def test_set_field_get(self):
		"""
		Try to save field of an object using GET request.
		"""
		url = reverse("theapp-set_field")

		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.content, _("Only POST request allowed"))

	def test_set_field_bad_params(self):
		"""
		Try to save field of an object via the view (bad parameters).
		"""
		url = reverse("theapp-set_field")

		self.create_objects()

		# without parameters
		response = self.client.post(url, {})
		self.assertEqual(response.status_code, 404)

		# bad model name
		response = self.client.post(url, {
			"model-name": "123",
			"field-name": "876",
			})
		self.assertEqual(response.status_code, 404)

		for model_cls in MODELS_LIST:
			# bad field name
			response = self.client.post(url, {
				"model-name": model_cls.__name__,
				"field-name": "876",
				})
			self.assertEqual(response.status_code, 404)

			for obj in model_cls.objects.all():
				for f in model_cls._meta.fields:
					# without id
					response = self.client.post(url, {
						"model-name": model_cls.__name__,
						"field-name": f.name,
						})
					self.assertEqual(response.status_code, 404)

					# bad id
					response = self.client.post(url, {
						"model-name": model_cls.__name__,
						"field-name": f.name,
						"id": obj.id + 1000,
						})
					self.assertEqual(response.status_code, 404)

					# without the required field
					response = self.client.post(url, {
						"model-name": model_cls.__name__,
						"field-name": f.name,
						"id": obj.id,
						})
					if f.name == "id":
						self.assertEqual(response.status_code, 404)
					else:
						self.assertEqual(response.status_code, 200)
						self.assertEqual(response.content,
								_("This field is required."))

					# invalid form data
					if f.__class__.__name__ in BADDATA_FIELDS:
						response = self.client.post(url, {
							"model-name": model_cls.__name__,
							"field-name": f.name,
							"id": obj.id,
							f.name: BADDATA_FIELDS[f.__class__.__name__][0]
							})

						should_be = BADDATA_FIELDS[f.__class__.__name__][1]
						if f.__class__.__name__ == "CharField":
							should_be = should_be % ({
								"limit_value": f.max_length,
								"show_value":
									len(BADDATA_FIELDS[f.__class__.__name__][0])
								})
						self.assertEqual(response.status_code, 200)
						self.assertEqual(response.content, should_be)

	def test_set_field(self):
		"""
		Try to save field of an object via the view.
		"""
		url = reverse("theapp-set_field")

		self.create_objects()
		for model_cls in MODELS_LIST:
			for obj in model_cls.objects.all():
				for f in model_cls._meta.fields:
					if f.__class__.__name__ in NEWDATA_FIELDS:
						response = self.client.post(url, {
							"model-name": model_cls.__name__,
							"field-name": f.name,
							"id": obj.id,
							f.name: NEWDATA_FIELDS[f.__class__.__name__]
							})
						self.assertEqual(response.status_code, 200)
						self.assertEqual(response.content, "")

			for obj in model_cls.objects.all():
				for f in model_cls._meta.fields:
					if f.__class__.__name__ in NEWDATA_FIELDS:
						should_be = NEWDATA_FIELDS[f.__class__.__name__]
						if f.__class__.__name__ == "DateField":
							dt = datetime.strptime(should_be, "%Y-%m-%d")
							should_be = date(dt.year, dt.month, dt.day)
						self.assertEqual(getattr(obj, f.name), should_be)

	def test_create_object_get(self):
		"""
		Try to create a model object using GET request.
		"""
		url = reverse("theapp-create_object")

		response = self.client.get(url)
		self.assertEqual(response.status_code, 200)
		self.assertEqual(response.content, _("Only POST request allowed"))

	def test_create_object_bad(self):
		"""
		Try to create a model object via the view (bad parameters).
		"""
		url = reverse("theapp-create_object")

		# without model-name
		response = self.client.post(url)
		self.assertEqual(response.status_code, 404)

		for model_cls in MODELS_LIST:
			# invalid form data
			data = {"model-name": model_cls.__name__}
			for f in model_cls._meta.fields:
				name = f.__class__.__name__
				if name in BADDATA_FIELDS:
					data[f.name] = BADDATA_FIELDS[name]
			response = self.client.post(url, data)

			self.assertEqual(response.status_code, 200)
			self.assertNotEqual(response.content, "")

			self.assertEqual(model_cls.objects.count(), 0)

	def test_create_object(self):
		"""
		Try to create a model object via the view.
		"""
		url = reverse("theapp-create_object")

		for model_cls in MODELS_LIST:
			data = {"model-name": model_cls.__name__}
			for f in model_cls._meta.fields:
				name = f.__class__.__name__
				if name in DATA_FIELDS:
					data[f.name] = DATA_FIELDS[name]
			response = self.client.post(url, data)
			self.assertEqual(response.status_code, 200)
			self.assertEqual(response.content, "")

			for obj in model_cls.objects.all():
				for f in model_cls._meta.fields:
					if f.__class__.__name__ in DATA_FIELDS:
						should_be = DATA_FIELDS[f.__class__.__name__]
						if f.__class__.__name__ == "DateField":
							dt = datetime.strptime(should_be, "%Y-%m-%d")
							should_be = date(dt.year, dt.month, dt.day)
						self.assertEqual(getattr(obj, f.name), should_be)

