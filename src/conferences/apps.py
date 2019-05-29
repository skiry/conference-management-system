from __future__ import unicode_literals
from django.apps import AppConfig


class ConferenceConfig(AppConfig):
    name = "conferences"
    verbose_name = "User Conferences"

    def ready(self):
        from . import signals  # noqa
