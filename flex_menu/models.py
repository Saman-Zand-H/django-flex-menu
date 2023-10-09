import logging
import re

from django.contrib.auth.models import Permission
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.functional import cached_property
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from mptt.models import MPTTModel, TreeForeignKey

from . import default_settings as app_settings
from .enums import MenuTypes
from .managers import MenuItemManager

logger = logging.getLogger()


class AbstractLocalized(models.Model):
    language = models.CharField(
        choices=app_settings.LANGUAGES, default="en", max_length=5
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Menu(AbstractLocalized):
    name = models.CharField(_("name"), max_length=50, unique=True)
    type = models.CharField(_("menu type"), choices=MenuTypes.choices, max_length=2)
    slug = models.SlugField(_("slug"), unique=True)
    attributes = models.JSONField(
        _("attributes"),
        default=dict,
    )
    icon = models.CharField(max_length=50, blank=True, null=True)
    enabled = models.BooleanField(_("enabled"), default=True)

    class Meta:
        verbose_name = _("Menu")
        verbose_name_plural = _("Menus")

    def __str__(self):
        return "{}".format(self.name)

    @property
    def parsed_attributes(self):
        return mark_safe("\n".join([f'{k}="{v}"' for k, v in self.attributes.items()]))


class MenuItem(MPTTModel, AbstractLocalized):
    label = models.CharField(
        _("label"), max_length=50, help_text=_("Display name on the website.")
    )
    slug = models.SlugField(
        _("slug"), unique=True, help_text=_("Unique identifier for the menu.")
    )
    menu = models.ForeignKey(
        Menu,
        on_delete=models.CASCADE,
        related_name="items",
        verbose_name=_("menu"),
    )
    parent = TreeForeignKey(
        "self",
        limit_choices_to={"level": 0},
        verbose_name=_("parent"),
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
    )
    link = models.CharField(_("link"), max_length=255, blank=True, default="#")
    order = models.IntegerField(_("order"))
    icon = models.CharField(_("icon"), max_length=50, blank=True, null=True)
    enabled = models.BooleanField(_("enabled"), default=True)
    login_required = models.BooleanField(
        _("login required"),
        default=False,
        help_text=_(
            "If this is checked, only logged-in users will be able to view the item."
        ),
    )
    permissions = models.ManyToManyField(
        Permission,
        verbose_name=_("permissions"),
        blank=True,
        help_text=_(
            "If empty, the menu item will be publicly visible, otherwise only users with at least one of the selected permissions could see it."  # noqa
        ),
    )
    no_reload = models.BooleanField(default=True)
    extras = models.CharField(
        _("extras"),
        max_length=255,
        blank=True,
        null=True,
        help_text=mark_safe(
            _(
                'Comma separated list of extra-attributes, e.g.: <code>icon="fa fa-user",data-tooltip="Go home!"</code>'
            )
        ),
    )

    objects = MenuItemManager()
    all_objects = models.Manager()

    active = False
    with_active = False

    def __str__(self):
        return "{}".format(self.label)

    class Meta:
        verbose_name = _("MenuItem")
        verbose_name_plural = _("MenuItems")
        ordering = ["order"]

    class MPTTMeta:
        order_insertion_by = ("order",)

    def clean(self):
        super().clean()
        if getattr(self.parent, "level", 0) > 0:
            raise ValidationError("Further nested menu is not supported.")

    @cached_property
    def has_children(self):
        return self.children.exists()

    def extras_dict(self):
        try:
            return dict(
                [re.sub("\"|'", "", i).strip() for i in s.split("=")]
                for s in self.extras.split(",")
            )
        except Exception:
            return {}
