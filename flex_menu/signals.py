from waffle.models import Flag

from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from .models import MenuItem


@receiver(post_save, sender=MenuItem)
def create_waffle_flag(sender, instance, created, **kwargs):
    if created:
        Flag.objects.get_or_create(name=instance.slug)


@receiver(post_delete, sender=MenuItem)
def delete_waffle_flag(sender, instance, **kwargs):
    Flag.objects.filter(name=instance.slug).delete()
