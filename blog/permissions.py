from rest_framework.generics import get_object_or_404
from rest_framework.permissions import BasePermission, SAFE_METHODS

from accounts.models import Profile, Relation


class IsPostAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method not in SAFE_METHODS:
            return request.user.is_authenticated and request.user.profile == obj.author
        return True


class IsCommentAuthor(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE':
            return request.user.is_authenticated and request.user.profile == obj.user

        return True


class IsVoter(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in ('DELETE', 'PUT'):
            return bool(request.user.is_authenticated and request.user.profile == obj.profile)

        return True


class HasPost(BasePermission):

    def has_permission(self, request, view):
        if request.method == 'POST':
            return bool(view.kwargs.get('slug', None))

        return True


class IsPublicOrFollowing(BasePermission):

    def has_permission(self, request, view):
        if view.kwargs.get('uid'):
            author = get_object_or_404(Profile, uid=view.kwargs.get('uid'))

            if not author.is_private:
                return True

            followings = author.followers.filter(
                state=Relation.RelationState.FOLLOWED
            ).values_list('actor', flat=True)

            return request.user.profile.id in (author.id, *tuple(followings))

        return True

    def has_object_permission(self, request, view, obj):
        if not obj.author.is_private:
            return True

        followings = obj.author.followers.filter(
            state=Relation.RelationState.FOLLOWED
        ).values_list('actor', flat=True)

        return request.user.profile.id in (obj.author.id, *tuple(followings))


class IsNotBlocked(BasePermission):
    def has_permission(self, request, view):
        if view.kwargs.get('uid'):
            author = get_object_or_404(Profile, uid=view.kwargs.get('uid'))

            # blocked = author.followers.filter(
            #     state=Relation.RelationState.BLOCKED
            # ).values_list('actor', flat=True)
            blocked = author.block_list()
            return request.user.profile.id not in tuple(blocked)

        return True

    def has_object_permission(self, request, view, obj):
        if view.kwargs.get('slug', None):
            blocked = obj.author.block_list().values_list('actor', flat=True)

            return request.user.profile not in tuple(blocked)

        return True
