from typing import Any

from mptt.admin import MPTTModelAdmin

from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.utils.translation import gettext_lazy as _

from .models import Menu, MenuItem


@admin.register(Menu)
class MenuAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "slug", "language", "type", "items"]
    list_editable = ["slug"]
    list_filter = ["type", "language"]

    def items(self, obj):
        return obj.items.count()


@admin.register(MenuItem)
class MenuItemAdmin(MPTTModelAdmin):
    list_display = (
        "slug",
        "label",
        "icon",
        "order",
        "menu",
        "link",
        "parent",
        "login_required",
        "enabled",
    )
    list_filter = (
        "parent",
        "enabled",
        "login_required",
    )
    list_editable = ["label", "icon", "order", "parent", "link", "enabled"]
    search_fields = ("label",)
    filter_horizontal = ("permissions",)
    prepopulated_fields = {"slug": ("label",)}
    fieldsets = (
        (
            _("Main"),
            {
                "fields": (
                    "menu",
                    "parent",
                    "label",
                    "slug",
                    "link",
                    "icon",
                    "order",
                    "extras",
                ),
                "description": _("A menu item without parent identifies a new menu."),
            },
        ),
        (
            _("Visibility"),
            {
                "fields": (
                    "enabled",
                    "login_required",
                    "permissions",
                ),
                "classes": ("tab-fs-permissions",),
                "description": _(
                    "Yuo can decide to disable or restrict the visibility of this voice and consequently of all its children. Keep in mind that also if a child is publicly visible, but this voice requires a login, then the child will not be visible to not logged users. The same happens for permissions restrictions."
                ),
            },
        ),
    )

    def get_queryset(self, request):
        qs = self.model.all_objects.all()

        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs
