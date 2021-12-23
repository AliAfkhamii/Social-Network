from rest_framework.decorators import api_view, action
from rest_framework.exceptions import PermissionDenied, NotFound
from rest_framework.generics import get_object_or_404
from rest_framework.mixins import RetrieveModelMixin, DestroyModelMixin, ListModelMixin, UpdateModelMixin
from rest_framework.views import Response
from rest_framework.viewsets import GenericViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.status import HTTP_200_OK, HTTP_403_FORBIDDEN

from .serializers import *
from .permissions import IsProfileOwner

profile_owner_actions = ('requests', 'followers', 'followings', 'block_list')


class ProfileViewSet(RetrieveModelMixin,
                     UpdateModelMixin,
                     DestroyModelMixin,
                     ListModelMixin,
                     GenericViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    lookup_field = "uid"
    lookup_url_kwarg = "uid"

    # permission_classes = (IsAuthenticated & IsProfileOwner,)

    def get_permissions(self):
        if self.action not in profile_owner_actions:
            return IsAuthenticated(),

        return IsAuthenticated(), IsProfileOwner(),

    @action(methods=('post',), detail=True)
    def follow(self, request, uid=None):
        instance = request.user.profile
        account = self.get_object()
        if instance == account:
            raise PermissionDenied("users can't follow themselves")

        relationship, created = Relation.objects.get_or_create(actor=instance, account=account)

        if not created:
            message = "can not send follow requests to this user while there is already a relationship between them"
            raise PermissionDenied(message)

        message = relationship.follow()
        return Response(data={'detail': message}, status=HTTP_200_OK)

    @action(methods=('post',), detail=True)
    def unfollow(self, request, uid=None):
        relationship = get_object_or_404(
            Relation, actor=request.user.profile, account=self.get_object(), state=Relation.RelationState.FOLLOWED
        )

        message = relationship.unfollow()
        return Response(data={'detail': message}, status=HTTP_200_OK)

    @action(methods=('post',), detail=True, url_path='undo-request')
    def undo_request(self, request, uid=None):
        relationship = get_object_or_404(
            Relation, actor=request.user.profile, account=self.get_object(), state=Relation.RelationState.REQUESTED
        )

        message = relationship.undo_req()
        return Response(data={'detail': message}, status=HTTP_200_OK)

    @action(methods=('POST',), detail=True)
    def block(self, request, uid=None):
        relationship, created = Relation.objects.get_or_create(actor=request.user.profile, account=self.get_object())
        if relationship.state == Relation.RelationState.BLOCKED:
            raise NotFound()
        message = relationship.block()
        return Response(data={'detail': message}, status=HTTP_200_OK)

    @action(methods=('POST',), detail=True)
    def unblock(self, request, uid=None):
        relationship = get_object_or_404(
            Relation, actor=request.user.profile, account=self.get_object(), state=Relation.RelationState.BLOCKED
        )
        message = relationship.unblock()
        return Response(data={'detail': message}, status=HTTP_200_OK)

    @action(methods=('post',), detail=True)
    def accept(self, request, uid=None):
        instance = self.get_object()
        account = request.user.profile
        relationship = get_object_or_404(
            account.followers.all(), actor=instance, state=Relation.RelationState.REQUESTED
        )

        message = relationship.accept()
        return Response(data={'detail': message}, status=HTTP_200_OK)

    @action(methods=('post',), detail=True)
    def decline(self, request, uid=None):
        instance = self.get_object()
        account = request.user.profile
        relationship = get_object_or_404(
            account.followers.all(), actor=instance, state=Relation.RelationState.REQUESTED
        )

        message = relationship.decline()
        return Response(data={'detail': message}, status=HTTP_200_OK)

    @action(methods=('post',), detail=False, url_path='change-privacy')
    def change_privacy(self, request, *args, **kwargs):
        profile = get_object_or_404(Profile, pk=self.request.user.id)
        profile.change_state()

        message = f'profile availability changed to {"Private" if profile.is_private else "Public"}'
        return Response(data={'detail': message}, status=HTTP_200_OK)

    @action(methods=('get',), detail=True, serializer_class=RequestSerializer)
    def requests(self, request, uid=None):
        instance = request.user.profile
        if not instance.is_private:
            message = "a Public profile Does Not have follow requests"
            return Response(data={'detail': message}, status=HTTP_403_FORBIDDEN)

        serializer = RequestSerializer(instance=instance, context={'request': request})
        return Response(data=serializer.data, status=HTTP_200_OK)

    @action(methods=('get',), detail=True, serializer_class=FollowersSerializer)
    def followers(self, request, uid=None):
        instance = request.user.profile
        serializer = self.get_serializer(instance=instance, context={'request': request})
        return Response(data=serializer.data, status=HTTP_200_OK)

    @action(methods=('get',), detail=True, serializer_class=FollowingsSerializer)
    def followings(self, request, uid=None):
        instance = request.user.profile
        serializer = self.get_serializer(instance=instance, context={'request': request})
        return Response(data=serializer.data, status=HTTP_200_OK)

    @action(methods=('get',), detail=True, serializer_class=BlockListSerializer, url_path='block-list')
    def block_list(self, request, uid=None):
        instance = request.user.profile
        serializer = self.get_serializer(instance=instance, context={'request': request})
        return Response(data=serializer.data, status=HTTP_200_OK)

    @action(methods=('get', 'put'), detail=False, serializer_class=UserOwnerSerializer, url_path='settings')
    def more_settings(self, request):
        instance = request.user
        if request.method == 'GET':
            serializer = self.get_serializer(instance=instance, context={'request': request})
            return Response(data=serializer.data, status=HTTP_200_OK)
        elif request.method == 'PUT':
            serializer = self.get_serializer(instance=instance, data=request.data, partial=True)
            serializer.save()
            return Response(serializer.data, status=HTTP_200_OK)

    @action(methods=('post',), detail=False, serializer_class=UserRegistrationSerializer)
    def register(self, request):
        # if request.user.is_authenticated:
        #     raise PermissionDenied(f'{request.user} has already registered')

        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        data = {**serializer.data, **{'Token': f'{user.auth_token}'}}
        return Response(data=data, status=HTTP_200_OK)


@api_view(('POST',))
def logout(request):
    request.user.auth_token.delete()
    return Response(data={'message': 'logged out successfully'})
