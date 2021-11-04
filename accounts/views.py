from django.shortcuts import render
from rest_framework.decorators import api_view
from rest_framework.views import Response
# from rest_framework.authtoken.views import ObtainAuthToken
# from .serializers import EmailTokenAuthentication


# class Login(ObtainAuthToken):
#     serializer_class = EmailTokenAuthentication


@api_view
def logout(request):
    if request.method == 'POST':
        request.user.auth_token.delete()
        return Response(data={'message': 'logged out successfully'})


def profile(request):
    Response('message')
