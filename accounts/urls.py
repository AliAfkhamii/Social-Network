from django.urls import path, include
from rest_framework.routers import SimpleRouter

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from .views import ProfileViewSet, RegisterAPIView
from blog.views import PostViewSet

app_name = 'accounts'

router = SimpleRouter()
router.register(r'profile', ProfileViewSet, basename='profile')

urlpatterns = [
    path('', include(router.urls)),
    path('profile/<str:uid>/posts/', PostViewSet.as_view({'get': 'list'}), name='profile-posts'),

    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterAPIView.as_view(), name='register'),
]
