from .signals import object_viewed


class ObjectHitMixin:
    view_object = None

    def get(self, request, *args, **kwargs):
        """it's written for compatibility with the other types of views which are not necessarily ViewSet types"""

        self.retrieve(request, *args, respond=False, **kwargs)
        return super().get(request, *args, *kwargs)

    def retrieve(self, request, *args, respond=True, **kwargs):
        """
        simply sends a signal to track the hit information to the object it's being retrieved

        this function somehow manipulates the retrieve function in drf mixins so that it forces the view to run this
        function first.
        """
        instance = self.view_object or self.get_object()  # defaults to 'get_object' method in GenericAPIView

        object_viewed.send(sender=instance.__class__, instance=instance, request=request)

        if respond:
            return super().retrieve(self, request, *args, **kwargs)
