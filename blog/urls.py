from django.urls import path, include
from rest_framework import routers

from .views import PostViewSet, CommentList, CommentDetailDestroy

app_name = 'blog'

router = routers.SimpleRouter()
router.register(r'posts', PostViewSet)

# router.register(r'likes', views.LikeViewSet, basename='likes')

urlpatterns = [
    path('', include(router.urls)),
    # path('posts/<slug:slug>/likes/', LikeAPIView.as_view(), name='post-likes'),
    path('posts/<slug:slug>/comments/', CommentList.as_view(), name='comment-list'),
    path('comments/<int:pk>/', CommentDetailDestroy.as_view(), name='comment-detail-destroy'),
]
