import logging

from django import template
from django.template.base import token_kwargs
from django.template.loader import get_template
from django.urls import reverse

from ..enums import MenuTypes
from ..models import Menu, MenuItem

register = template.Library()
logger = logging.getLogger(__name__)


def flatten_nested_context(context, parent_key=""):
    flattened_dict = {}
    for item in context:
        if issubclass(item.__class__, template.context.BaseContext):
            nested_dict = flatten_nested_context(reversed(item.dicts), parent_key)
            flattened_dict.update(nested_dict)
        elif isinstance(item, dict):
            for key, value in item.items():
                new_key = f"{parent_key}.{key}" if parent_key else key
                flattened_dict[new_key] = value
        else:
            flattened_dict[parent_key] = item

    return flattened_dict


class MenuNode(template.Node):
    def __init__(self, nodeslist, extra_context):
        super().__init__()
        self.extra_context = extra_context
        self.nodeslist = nodeslist

    def render(self, context):
        resolved_context = {
            name: var.resolve(context) for name, var in self.extra_context.items()
        }
        base_template = get_template("flex_menu/navigation_menu.html")
        items = self.nodeslist.render(context)
        resolved_context["menu_active"] = "cursor-pointer active" in items
        context.update({**resolved_context, "menu_items": items})
        return base_template.render(flatten_nested_context(context.dicts))


@register.tag
def navigation_menu(parser, token):
    """
    TODO: Usage should be included in here
    """
    bits = token.split_contents()
    if len(bits) < 3:
        raise template.TemplateSyntaxError(
            "navigation_menu tag takes at least 2 arguments."
        )

    options = {}
    remaining_bits = bits[1:]
    while remaining_bits:
        option = remaining_bits.pop(0)
        if option == "with":
            value = token_kwargs(remaining_bits, parser, support_legacy=False)
            if not value:
                raise template.TemplateSyntaxError(
                    "With requires at least one argument."
                )
            options[option] = value

    namemap = options.get("with", {})
    nodelist = parser.parse(("endnavigation_menu",))
    parser.delete_first_token()

    return MenuNode(nodeslist=nodelist, extra_context=namemap)


class HtmxLinkNode(template.Node):
    def __init__(self, nodeslist, extra_context):
        super().__init__()
        self.nodeslist = nodeslist
        self.extra_context = extra_context

    def render(self, context):
        base_template = get_template("flex_menu/link.html")
        items = self.nodeslist.render(context)
        resolved_context = {
            name: var.resolve(context) for name, var in self.extra_context.items()
        }
        context.update({**resolved_context, "content": items})
        return base_template.render(flatten_nested_context(context.dicts))


@register.tag
def link(parser, token):
    bits = token.split_contents()
    if len(bits) < 3:
        raise template.TemplateSyntaxError(
            "navigation_menu tag takes at least 1 arguments."
        )

    options = {}
    remaining_bits = bits[1:]
    while remaining_bits:
        option = remaining_bits.pop(0)
        if option == "with":
            value = token_kwargs(remaining_bits, parser, support_legacy=False)
            if not value:
                raise template.TemplateSyntaxError(
                    "With requires at least one argument."
                )
            options[option] = value

    namemap = options.get("with", {})
    if "href" not in namemap:
        raise template.TemplateSyntaxError("href is a required argument.")

    nodelist = parser.parse(("endlink",))
    parser.delete_first_token()

    return HtmxLinkNode(nodeslist=nodelist, extra_context=namemap)


@register.inclusion_tag("flex_menu/navigation_link.html", takes_context=True)
def navigation_link(context, *, item):
    if not isinstance(item, MenuItem):
        raise ValueError(f"item must be a MenuItem instance {type(item)}.")

    context.update(
        {
            "navigation_title": item.label,
            "navigation_icon": item.icon,
            "navigation_link": reverse(item.link),
            "navigation_extras": item.extras,
            "navigation_no_reload": item.no_reload,
            "navigation_is_active": context.request.resolver_match.view_name
            == item.link,
            "is_menuitem": item.parent is not None,
        }
    )
    return context


@register.inclusion_tag("flex_menu/menu.html", takes_context=True)
def load_navbar(context, menu_slug: str):
    if (menu_qs := Menu.objects.filter(slug=menu_slug, type=MenuTypes.NAVBAR)).exists():
        context.update({"menu": menu_qs.first()})
        return context

    raise ValueError(f"Menu with slug {menu_slug} does not exist.")


@register.inclusion_tag("flex_menu/sidebar.html", takes_context=True)
def load_sidebar(context, menu_slug: str):
    if (
        menu_qs := Menu.objects.filter(slug=menu_slug, type=MenuTypes.SIDEBAR)
    ).exists():
        context.update({"menu": menu_qs.first()})
        return context

    return context.update({"menu": Menu.objects.none()})
