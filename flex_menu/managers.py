from mptt.managers import TreeManager


class MenuItemManager(TreeManager):
    def get_queryset(self, *args, **kwargs):
        return super().get_queryset(*args, **kwargs).filter(enabled=True)

    def roots(self, *args, **kwargs):
        return self.filter(level=0)
