"""
The settings for 'theapp' application.
"""

import os
from django.conf import settings

THEAPP_MODELS_YAML_CONFIG = getattr(settings, "THEAPP_MODELS_YAML_CONFIG",
		os.path.join(settings.BASE_DIR, "theapp", "models.yaml"))

