from django.apps import AppConfig


class FlexMenuConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "flex_menu"

    def ready(self):
        from . import signals
