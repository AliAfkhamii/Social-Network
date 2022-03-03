from rest_framework.generics import (
    RetrieveDestroyAPIView, ListCreateAPIView, CreateAPIView, ListAPIView, get_object_or_404
)

from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet

from accounts.models import Profile
from .serializers import (
    PostSerializer, VoteSerializer, CommentListSerializer, CommentRetrieveSerializer  # , ReplyRetrieveSerializer
)
from .permissions import (
    IsVoter, IsPublicOrFollowing, IsNotBlocked, IsPostAuthor, IsCommentAuthorDeletionOrIsAdmin,
    CommentIsPostAuthor
)
from .models import Post, Vote, Comment
from .utils import is_url
from analytics.mixins import ObjectHitMixin


class PostViewSet(ObjectHitMixin, ModelViewSet):
    serializer_class = PostSerializer
    lookup_field = 'slug'
    permission_classes = (IsAuthenticated, IsNotBlocked, IsPublicOrFollowing, IsPostAuthor,)

    def get_queryset(self):
        user_profile = self.request.user.profile

        if not is_url(self.request, url_name='profile-posts') and not is_url(self.request, url_name='post-detail'):
            return user_profile.posts.all()

        if is_url(self.request, url_name='profile-posts'):
            return get_object_or_404(Profile, uid=self.kwargs.get('uid')).posts.all()

        return Post.objects.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user.profile)


class FeedAPIView(ListAPIView):
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user_followings = self.request.user.profile.profile_followings()
        return Post.objects.filter(author__in=user_followings)


class CommentList(ListCreateAPIView):
    serializer_class = CommentListSerializer
    lookup_url_kwarg = 'slug'

    def get_queryset(self):
        return Comment.objects.filter(post__slug=self.kwargs.get(self.lookup_url_kwarg))

    def perform_create(self, serializer):
        post = Post.objects.get(slug=self.kwargs.get(self.lookup_url_kwarg))
        serializer.save(
            user=self.request.user.profile,
            post=post,
        )


class CompleteCommentList(ListAPIView):  # list of all Comments for administration purposes
    queryset = Comment.objects.all()
    serializer_class = CommentListSerializer
    permission_classes = IsAdminUser,


class CommentDetailDestroy(ObjectHitMixin, RetrieveDestroyAPIView, CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentRetrieveSerializer
    lookup_field = "pk"
    lookup_url_kwarg = "pk"

    def get_permissions(self):
        if self.request.method == 'DELETE':
            return IsCommentAuthorDeletionOrIsAdmin(),

        return super(CommentDetailDestroy, self).get_permissions()

    def perform_create(self, serializer):
        comment = self.get_object()
        other_fields = {
            'user': self.request.user.profile,
            'post': comment.post,
            'parent': comment,
        }
        serializer.save(**other_fields)


class ReplyList(ListAPIView):
    serializer_class = CommentRetrieveSerializer
    lookup_url_kwarg = "pk"

    def get_queryset(self):
        return get_object_or_404(Comment, pk=self.kwargs.get(self.lookup_url_kwarg)).replies.all()


class PinCommentAPIView(APIView):
    permission_classes = (CommentIsPostAuthor,)
    lookup_url_kwarg = 'pk'

    def post(self, request, *args, **kwargs):
        instance = get_object_or_404(Comment, pk=self.kwargs.get(self.lookup_url_kwarg))
        self.check_object_permissions(request, instance)
        instance.toggle_pin_Comment()
        return Response({'detail': f'Comment {"pinned" if instance.is_pinned else "unpinned"}'})


class VoteViewSet(ObjectHitMixin, ModelViewSet):
    serializer_class = VoteSerializer
    lookup_field = "pk"
    lookup_url_kwarg = "pk"
    permission_classes = (IsVoter,)

    def get_queryset(self):
        if is_url(self.request, url_name='vote-list'):
            return Vote.objects.filter(post__slug=self.kwargs.get('slug'))

        return Vote.objects.all()
