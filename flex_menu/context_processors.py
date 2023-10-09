from .default_settings import app_settings


def template_settings_processor(request):
    return {"template_settings": app_settings.TEMPLATE_SETTINGS}
