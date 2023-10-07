from django.db import models


class MenuTypes(models.TextChoices):
    SIDEBAR = "sb", "Sidebar"
    NAVBAR = "nb", "Navbar"
