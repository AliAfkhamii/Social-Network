from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsProfileOwner(BasePermission):

    def has_object_permission(self, request, view, obj):
        from .views import profile_owner_actions
        if request.method not in SAFE_METHODS or view.action in profile_owner_actions:
            return bool(request.user == obj.user)

        return True
