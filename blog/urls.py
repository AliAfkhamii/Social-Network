from django.urls import path, include
from rest_framework import routers

from .views import PostViewSet, LikeAPIView

router = routers.SimpleRouter()
router.register(r'posts', PostViewSet, basename='posts')

# router.register(r'likes', views.LikeViewSet, basename='likes')
from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view
def test(request):
    from .models import Post
    print('user :', request.user)
    obj = Post.objects.create(**request.data)
    return Response('Done... object : ', obj)


urlpatterns = [
    path('', include(router.urls)),
    path('posts/<slug:slug>/likes/', LikeAPIView.as_view(), name='post-likes'),
    path('test/', test, name='test'),
]
