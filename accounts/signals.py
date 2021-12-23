from django.db.models import Q
from django.dispatch import receiver, Signal
from django.db.models.signals import post_save, post_delete
from rest_framework.authtoken.models import Token

from .models import User, Profile, Relation

profile_state_changed = Signal()
profile_blocked = Signal()


@receiver(profile_state_changed, sender=Profile)
def accept_requested_profiles_as_followed(sender, instance, *args, **kwargs):
    requests = Relation.objects.filter(account=instance, state=Relation.RelationState.REQUESTED)
    for relation in requests:
        relation.state = Relation.RelationState.FOLLOWED
        relation.save()


@receiver(profile_blocked, sender=Relation)
def terminate_reversed_relations(sender, instance, *args, **kwargs):
    try:
        rel = sender.objects.get(~Q(state=sender.RelationState.BLOCKED), actor=instance.account, account=instance.actor)
    except sender.DoesNotExist:
        return

    rel._terminate_relation()


@receiver(post_save, sender=User)
def create_profile_and_Token(sender, instance, created, **kwargs):
    """
    creates related profile the first time a user signs in
    """
    if created:
        Profile.objects.create(user=instance)
        Token.objects.create(user=instance)


@receiver(post_delete, sender=Profile)
def delete_user(sender, instance, **kwargs):
    """
    deletes the user object/record when the related profile gets deleted
    """
    user = instance.user
    user.delete()
