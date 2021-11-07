from rest_framework.generics import get_object_or_404, GenericAPIView, ListAPIView, RetrieveDestroyAPIView, ListCreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED
from rest_framework.exceptions import NotFound

from .serializers import PostSerializer, LikeSerializer, CommentListSerializer, CommentRetrieveSerializer
from .models import Post, Like, Comment


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = 'slug'
    # permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


# class CommentList(ListAPIView):
#     serializer_class = CommentListSerializer
#     permission_classes = (AllowAny,)
#     # lookup_field = 'pk'
#
#     def get_queryset(self):
#         return Comment.objects.filter(post__slug=self.kwargs.get('slug'))


class CommentList(ListCreateAPIView):
    serializer_class = CommentListSerializer
    permission_classes = (AllowAny,)
    # lookup_field = 'pk'

    def get_queryset(self):
        return Comment.objects.filter(post__slug=self.kwargs.get('slug'))


class CommentDetailDestroy(RetrieveDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentRetrieveSerializer
    permission_classes = (AllowAny,)
    lookup_field = "pk"
