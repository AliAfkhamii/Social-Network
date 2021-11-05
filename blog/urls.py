from django.urls import path, include
from rest_framework import routers

from .views import PostViewSet, LikeAPIView

router = routers.SimpleRouter()
router.register(r'posts', PostViewSet, basename='posts')

# router.register(r'likes', views.LikeViewSet, basename='likes')


urlpatterns = [
    path('', include(router.urls)),
    path('posts/<slug:slug>/likes/', LikeAPIView.as_view(), name='post-likes'),
]
