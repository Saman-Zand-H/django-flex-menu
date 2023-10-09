from django.conf import settings
from django.utils.safestring import mark_safe

LANGUAGES = getattr(settings, "Languages", [("en", "English"), ("fa", "Farsi")])
TEMPLATE_SETTINGS = {
    "a_navigation_htmx": (
        'hx-swap="multi:#page-body:outerHTML,#navigation-bar:outerHTML,#jsScripts:outerHTML,#modals:outerHTML,#cssStyles:outerHTML" '
        'hx-push-url="true" hx-indicator="#page-loading" hx-boost="true"'
    ),
}

TEMPLATE_SETTINGS = {key: mark_safe(value) for key, value in TEMPLATE_SETTINGS.items()}
TEMPLATE_SETTINGS = getattr(settings, "TEMPLATE_SETTINGS", TEMPLATE_SETTINGS)
