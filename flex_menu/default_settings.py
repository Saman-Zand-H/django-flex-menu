from django.conf import settings
from django.utils.safestring import mark_safe


class AppSettings:
    def __init__(self):
        self.settings = getattr(settings, "FLEX_MENU", {})
    
    @property
    def LANGUAGES(self):
        return self.settings.setdefault("LANGUAGES", [("en", "English"), ("fa", "Farsi")])
    
    @property
    def MAX_LEVEL(self):
        return self.settings.setdefault("MAX_LEVEL", 2)

    @property
    def TEMPLATE_SETTINGS(self):
        TEMPLATE_SETTINGS = {
            "a_navigation_htmx": (
                'hx-swap="multi:#page-body:outerHTML,#navigation-bar:outerHTML,#jsScripts:outerHTML,#modals:outerHTML,#cssStyles:outerHTML" '
                'hx-push-url="true" hx-indicator="#page-loading" hx-boost="true"'
            ),
        }

        TEMPLATE_SETTINGS = {key: mark_safe(value) for key, value in TEMPLATE_SETTINGS.items()}
        return self.settings.setdefault("TEMPLATE_SETTINGS", TEMPLATE_SETTINGS)
    

app_settings = AppSettings()
