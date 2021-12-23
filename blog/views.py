from rest_framework.generics import (
    RetrieveDestroyAPIView, ListCreateAPIView, CreateAPIView, ListAPIView, get_object_or_404
)

from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet

from accounts.models import Relation, Profile
from .serializers import (
    PostSerializer, VoteSerializer, CommentListSerializer, CommentRetrieveSerializer
)

from .models import Post, Vote, Comment
from .permissions import IsCommentAuthor, IsVoter, IsPublicOrFollowing, IsNotBlocked, IsPostAuthor


class PostViewSet(ModelViewSet):
    serializer_class = PostSerializer
    lookup_field = 'slug'
    permission_classes = (IsAuthenticated, IsNotBlocked, IsPublicOrFollowing, IsPostAuthor,)

    def get_queryset(self):
        request_profile = self.request.user.profile
        kwargs = self.kwargs.get
        uid, slug = kwargs('uid', None), kwargs('slug', None)

        if not uid and not slug:
            return request_profile.posts.all()

        if uid:
            return get_object_or_404(Profile, uid=uid).posts.all()

        return Post.objects.all()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user.profile)


class FeedAPIView(ListAPIView):
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        user_followings = self.request.user.profile.followings.filter(
            state=Relation.RelationState.FOLLOWED
        ).values_list('account', flat=True)

        return Post.objects.filter(author_id__in=user_followings)


class CommentList(ListCreateAPIView):
    serializer_class = CommentListSerializer

    def get_queryset(self):
        if slug := self.kwargs.get('slug'):
            return Comment.objects.filter(post__slug=slug)
        return Comment.objects.all()

    def get_permissions(self):
        if not self.kwargs.get('slug'):
            return IsAdminUser(),

        return super(CommentList, self).get_permissions()

    def perform_create(self, serializer):
        post = Post.objects.get(slug=self.kwargs.get('slug'))
        serializer.save(
            user=self.request.user.profile,
            post=post,
        )

    def post(self, request, *args, **kwargs):
        if self.kwargs.get('slug', None):
            return self.create(request, *args, **kwargs)
        return Response(data={'detail': '\'POST\' methods are not allowed'})


class CommentDetailDestroy(RetrieveDestroyAPIView, CreateAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentRetrieveSerializer
    lookup_field = "pk"
    lookup_url_kwarg = "pk"
    permission_classes = (IsCommentAuthor,)

    def perform_create(self, serializer):
        comment = self.get_object()
        other_fields = {
            'user': self.request.user.profile,
            'post': comment.post,
            'parent': comment,
        }
        serializer.save(**other_fields)


class VoteViewSet(ModelViewSet):
    serializer_class = VoteSerializer
    lookup_field = "pk"
    lookup_url_kwarg = "pk"
    permission_classes = (IsVoter,)

    def get_queryset(self):
        if slug := self.kwargs.get('slug'):
            return Vote.objects.filter(post__slug=slug)
        return Vote.objects.all()
