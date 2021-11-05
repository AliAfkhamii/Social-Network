from django.dispatch import receiver, Signal
from django.db.models.signals import pre_save

from .models import Post
from blog import utils
import uuid


@receiver(pre_save, sender=Post)
def slug_logic(sender, instance, *args, **kwargs):
    if (not instance.slug) or (instance.current_title != instance.title):
        # gets the field we want to slugify based on that
        indicator = instance.title or (instance.author, uuid.uuid4())

        exists, to_slug = utils.get_slug(instance, indicator)
        while exists:
            exists, to_slug = utils.get_slug(instance, indicator, uuid.uuid4())
        instance.slug = to_slug
        instance.current_title = instance.title

# post_like = Signal()
#
#
# @receiver(post_like, sender=Post)
# def apply_like_to_dependencies(sender, instance, profile, state, **kwargs):
#     pass

# view_triggered = Signal()
#
# @receiver(view_triggered)
# def track_views_on_posts(sender, )
