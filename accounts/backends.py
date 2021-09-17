from django.contrib.auth.backends import BaseBackend

from .models import User


class EmailBackend(BaseBackend):
    def authenticate(self, request, email=None, password=None, **kwargs):
        if email is None:
            email = request.user.email
        if email is None or password is None:
            return
        try:
            user = User.objects.get(email=email)
            pass_valid = user.check_password(password)
            return user if pass_valid and user.is_active else None
        except User.DoesNotExist:
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
