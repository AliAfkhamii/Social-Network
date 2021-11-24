from django.urls import path, include
from rest_framework import routers

from .views import PostViewSet, CommentList, CommentDetailDestroy, FeedAPIView, VoteViewSet

app_name = 'blog'

router = routers.SimpleRouter()
router.register(r'posts', PostViewSet, 'post')

vote_urls = [
    path('likes/', VoteViewSet, 'vote-list'),
    path('likes/<int:id>/', VoteViewSet, 'vote-detail')
]

urlpatterns = [
    path('', include(router.urls)),
    path('posts/<slug:slug>/votes/', VoteViewSet.as_view({'get': 'list', 'post': 'create'}), name='vote-list'),
    path('votes/<int:pk>/',
         VoteViewSet.as_view({'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}),
         name='vote-detail'),

    path('posts/<slug:slug>/comments/', CommentList.as_view(), name='comment-list'),
    path('comments/<int:pk>/', CommentDetailDestroy.as_view(), name='comment-detail'),
    path('comments/', CommentList.as_view(), name='comments-full-list'),

    path('feed/', FeedAPIView.as_view(), name='feed'),
]
