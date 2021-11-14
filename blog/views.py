from rest_framework.generics import (
    RetrieveDestroyAPIView, ListCreateAPIView, CreateAPIView, ListAPIView
)

from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED
from rest_framework.exceptions import NotFound

from .serializers import PostSerializer, LikeSerializer, CommentListSerializer, CommentRetrieveSerializer
from .models import Post, Like, Comment
from .permissions import DeletionIsCommentAuthor


class PostViewSet(ModelViewSet):
    serializer_class = PostSerializer
    lookup_field = 'slug'
    queryset = Post.objects.filter(author__private=False)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user.profile)


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
    permission_classes = (DeletionIsCommentAuthor,)

    def perform_create(self, serializer):
        comment = self.get_object()
        other_fields = {
            'user': self.request.user.profile,
            'post': comment.post,
            'parent': comment,
        }
        serializer.save(**other_fields)
