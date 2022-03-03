from rest_framework.generics import get_object_or_404
from rest_framework.permissions import BasePermission, SAFE_METHODS, IsAdminUser

from accounts.models import Profile
from blog.models import Post
from blog.utils import is_url


class IsPostAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method not in SAFE_METHODS:
            return request.user.is_authenticated and request.user.profile == obj.author
        return True


class CommentIsPostAuthor(BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.profile == obj.post.author


class IsCommentAuthor(BasePermission):

    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and request.user.profile == obj.user


class IsCommentAuthorDeletionOrIsAdmin(IsCommentAuthor, IsAdminUser):
    def has_object_permission(self, request, view, obj):
        if request.method == 'DELETE':
            return super(IsAdminUser, self).has_permission(request, view) or \
                   super(IsCommentAuthor, self).has_object_permission(request, view, obj)


class IsVoter(BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method in ('DELETE', 'PUT'):
            return request.user.is_authenticated and request.user.profile == obj.profile

        return True


class IsPublicOrFollowing(BasePermission):

    def has_permission(self, request, view):
        if is_url(request, url_name='profile-posts'):
            author = get_object_or_404(Profile, uid=view.kwargs.get('uid'))

            if not author.is_private:
                return True

            followings = author.profile_followings()

            return request.user.profile in (author, *followings)

        return True

    def has_object_permission(self, request, view, obj):
        if not obj.author.is_private:
            return True

        followings = obj.author.profile_followers()

        return request.user.profile in (obj.author, *followings)


class IsNotBlocked(BasePermission):
    def has_permission(self, request, view):
        if is_url(request, url_name='profile-posts'):
            author = get_object_or_404(Profile, uid=view.kwargs.get('uid'))

            blocked = author.block_list()
            return request.user.profile.id not in tuple(blocked)

        return True

    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Post):
            blocked = obj.author.block_list().values_list('actor', flat=True)

            return request.user.profile not in tuple(blocked)

        return True
