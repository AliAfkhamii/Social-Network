from django.dispatch import receiver, Signal
from django.db.models.signals import pre_save

from .models import Post
from blog import utils
import uuid


@receiver(pre_save, sender=Post)
def slug_logic(sender, instance, *args, **kwargs):
    if (not instance.slug) or (instance.current_title != instance.title):
        # gets the field we want to slugify based on that
        indicator = instance.title or (uuid.uuid4(), instance.author)

        exists, to_slug = utils.get_slug(instance, indicator)
        while exists:
            exists, to_slug = utils.get_slug(instance, uuid.uuid4(), indicator)
        instance.slug = to_slug
        instance.current_title = instance.title
