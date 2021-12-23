from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.routers import SimpleRouter

from .views import logout, ProfileViewSet
from blog.views import PostViewSet

app_name = 'accounts'

router = SimpleRouter()
router.register(r'profile', ProfileViewSet, basename='profile')

urlpatterns = [
    path('', include(router.urls)),
    path('profile/<str:uid>/posts/', PostViewSet.as_view({'get': 'list'}), name='profile-posts'),
    path('login/', obtain_auth_token, name='login'),
    path('logout/', logout, name='logout'),
]
