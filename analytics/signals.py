from django.dispatch import receiver, Signal

from .models import LOGGER_MODEL, ContentType

object_viewed = Signal()


@receiver(object_viewed)
def save_user_info_to_object_hit(sender, instance, request, *args, **kwargs):
    """saves the user information viewed the specific object"""
    LOGGER_MODEL.objects.create(
        user=request.user,
        ip=request.ip_address,
        content_type=ContentType.objects.get_for_model(sender),
        object_id=instance.id,
        content_object=instance
    )
