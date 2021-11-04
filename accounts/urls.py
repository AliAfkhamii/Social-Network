from django.urls import path

# from .views import logout, profile
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('login/', obtain_auth_token, name='login'),
    # path('profile/', profile),
    # path('logout/', logout, 'logout'),
    # path('signup/', sign_up, 'sign_up'),
]
