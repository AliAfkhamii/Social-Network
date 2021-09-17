from django.dispatch import receiver
from django.db.models.signals import post_save, post_delete

from .models import User, Profile


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
