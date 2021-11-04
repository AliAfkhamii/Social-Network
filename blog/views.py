from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED
from rest_framework.exceptions import NotFound

from .serializers import PostSerializer, LikeSerializer
from .models import Post, Like


class PostViewSet(ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = 'slug'
    # permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


# class LikeViewSet(ModelViewSet):
#     # queryset = Like.objects.all()
#     serializer_class = LikeSerializer
#     lookup_field = 'post'
#     lookup_url_kwarg = 'value'
#
#     def get_queryset(self):
#         return Like.objects.filter(post=self.kwargs.get('post_id'))

class LikeAPIView(APIView):

    def get(self, request, *args, **kwargs):
        related_likes = Like.objects.filter(post__slug=kwargs.get('slug'))

        if not related_likes:
            raise NotFound()

        serializer = LikeSerializer(instance=related_likes, many=True)
        return Response(data=serializer.data, status=HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        profile = request.user.profile
        serializer = LikeSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)
        serializer.save(profile={
            profile.id,
            profile.user,
            profile.picture,
            profile.bio,
            }
        )
        return Response(serializer.data, status=HTTP_201_CREATED)
