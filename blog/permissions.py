from rest_framework.permissions import BasePermission


class IsPostAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE':
            return request.user.is_authenticated and (request.user.profile == obj.author or request.user.is_admin)

        return True


class IsCommentAuthor(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE':
            return request.user.is_authenticated and (request.user.profile == obj.user or request.user.is_admin)

        return True


class IsVoter(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in ('DELETE', 'PUT'):
            return bool(request.user.is_authenticated and request.user.profile == obj.profile)

        return True
