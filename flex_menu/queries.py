from django.core.cache import cache
from django.contrib.postgres.aggregates import ArrayAgg

from .models import MenuItem
from .default_settings import app_settings


def get_menu_items(menu):
    if cache.has_key(app_settings.MENU_ITEMS_CACHE_KEY):
        return cache.get(app_settings.MENU_ITEMS_CACHE_KEY)
    
    menu_items = list(MenuItem.objects.prefetch_related("children").filter(menu=menu, level=0).annotate(children_lst=ArrayAgg("children")).values())
    cache.set(
        app_settings.MENU_ITEMS_CACHE_KEY,
        menu_items,
        app_settings.MENU_ITEMS_CACHE_TIMEOUT,
    )
    return menu_items
