from rest_framework.generics import (
    RetrieveDestroyAPIView, ListCreateAPIView, CreateAPIView, ListAPIView
)

from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.viewsets import ModelViewSet
from django.db.models import Q

from .serializers import (
    PostSerializer, VoteSerializer, CommentListSerializer, CommentRetrieveSerializer
)

from .models import Post, Vote, Comment
from .permissions import IsCommentAuthor, IsVoter, IsPostAuthor


class PostViewSet(ModelViewSet):
    serializer_class = PostSerializer
    lookup_field = 'slug'
    permission_classes = (IsPostAuthor, IsAuthenticated,)

    def get_queryset(self):
        user_followings = self.request.user.profile.followings.values_list('account', flat=True)

        return Post.objects.filter(
            Q(author__private=False) | Q(author_id__in=user_followings)
        ).distinct()

    def perform_create(self, serializer):
        serializer.save(author=self.request.user.profile)

    def get_permissions(self):
        if self.action == 'create':
            return IsAuthenticated(),

        return super(PostViewSet, self).get_permissions()


class FeedAPIView(ListAPIView):
    serializer_class = PostSerializer

    def get_queryset(self):
        user_followings = self.request.user.profile.followings.values_list('account', flat=True)
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


# class VoteList(ListAPIView):
#     serializer_class = VoteSerializer
#
#     def get_queryset(self):
#         slug = self.kwargs.get('slug')
#         return Vote.objects.filter(post__slug=slug)
#
#
# class VoteCreateDetailDestroy(CreateAPIView, RetrieveDestroyAPIView):
#     serializer_class = VoteSerializer
#     lookup_field = "pk"
#     lookup_url_kwarg = "pk"
#     permission_classes = (IsVoter,)
#
#     def get_queryset(self):
#         slug = self.kwargs.get('slug')
#         return Vote.objects.filter(post__slug=slug)
#
#     def perform_create(self, serializer):
#         vote = self.get_object()
#         other_fields = {
#             'profile': self.request.user.profile,
#             'post': vote.post,
#         }
#         serializer.save(**other_fields)

class VoteViewSet(ModelViewSet):
    serializer_class = VoteSerializer
    lookup_field = "pk"
    lookup_url_kwarg = "pk"
    permission_classes = (IsVoter,)

    def get_queryset(self):
        if slug := self.kwargs.get('slug'):
            return Vote.objects.filter(post__slug=slug)
        return Vote.objects.all()

    def perform_create(self, serializer):
        vote = self.get_object()
        other_fields = {
            'profile': self.request.user.profile,
            'post': vote.post,
        }
        serializer.save(**other_fields)
