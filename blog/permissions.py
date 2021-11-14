from rest_framework.permissions import BasePermission


class DeletionIsCommentAuthor(BasePermission):
    def has_permission(self, request, view):
        return super(DeletionIsCommentAuthor, self).has_permission(request, view)

    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE':
            return bool(request.user.is_authenticated and request.user.profile == obj.user)

        return True
