from .default_settings import TEMPLATE_SETTINGS


def template_settings_processor(request):
    return {"template_settings": TEMPLATE_SETTINGS}
