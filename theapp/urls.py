
from django.conf.urls import patterns, url

urlpatterns = patterns(
		'',
		url(r'^$', "theapp.views.index", name="theapp-index"),
		url(r'^content/$', "theapp.views.get_content", name="theapp-get_content"),
		url(r'^save/$', "theapp.views.set_field", name="theapp-set_field"),
		url(r'^create/$', "theapp.views.create", name="theapp-create_object"),
		)

