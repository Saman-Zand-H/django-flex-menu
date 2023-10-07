import django
from django.conf import settings

LANGUAGES = getattr(settings, "Languages", [("en", "English"), ("fa", "Farsi")])
