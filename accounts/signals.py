from django.dispatch import receiver, Signal
from django.db.models.signals import post_save, post_delete

from .models import User, Profile

# profile_state_changed = Signal()
#
#
# @receiver(profile_state_changed, sender=Profile)
# def apply_public_state_to_relations(sender, instance, *args, **kwargs):
#     for rel in instance.followers.all():
#         rel.change_type()


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    """
    creates related profile the first time a user signs in
    """
    if created:
        Profile.objects.create(user=instance)


@receiver(post_delete, sender=Profile)
def delete_user(sender, instance, **kwargs):
    """
    deletes the user object/record when the related profile gets deleted
    """
    user = instance.user
    user.delete()
