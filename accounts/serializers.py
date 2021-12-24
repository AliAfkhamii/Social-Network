import rest_framework.exceptions
from rest_framework import serializers

from blog.models import Post
from .models import User, Profile, Relation


class UserRegistrationSerializer(serializers.HyperlinkedModelSerializer):
    password2 = serializers.CharField(write_only=True, label='confirm password', style={'input_type': 'password'})

    class Meta:
        model = User
        fields = ('email', 'username', 'password', 'password2', 'first_name', 'last_name',)
        extra_kwargs = {'password': {'write_only': True}}

    def validate_email(self, val):
        if self.Meta.model.objects.filter(email=val).exists():
            raise rest_framework.exceptions.ValidationError("user with this email address already exists")
        return val

    def validate(self, data):
        p1 = data.get('password')
        p2 = data.pop('password2')   # pops password2 here for validations, before it gets included to validated data.
        if not p1 or not p2 or p1 != p2:
            raise rest_framework.exceptions.ValidationError("passwords must match")

        return data

    def save(self, **kwargs):
        password = self.validated_data.pop('password')

        user = super(UserRegistrationSerializer, self).save(**kwargs)
        user.set_password(password)
        user.save()
        return user


class UserOwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ("password", "user_permissions", "groups", "id", "is_active", "is_staff", "is_superuser",)
        read_only_fields = (
            "email",
            "last_login",
            "date_joined",
        )


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "username",
            "phone",
            "date_joined",
            "first_name",
            "last_name",
        )
        read_only_fields = ("username",)
        extra_kwargs = {
            "phone": {'write_only': True}
        }


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    user = UserSerializer(read_only=True)
    relation = serializers.SerializerMethodField(method_name='get_state')
    num_posts = serializers.SerializerMethodField(method_name='get_num_posts')

    class Meta:
        model = Profile
        fields = (
            'url',
            'user',
            'picture',
            'bio',
            'website',
            'private',
            'relation',
            'num_posts',
        )
        extra_kwargs = {
            "url": {"view_name": "accounts:profile-detail", "lookup_field": "uid", },
        }

    def get_state(self, obj):
        try:
            relation = Relation.objects.get(account=obj, actor=self.context.get('request').user.profile)
            return relation.state
        except Relation.DoesNotExist:
            pass

    def get_num_posts(self, obj):
        return Post.objects.filter(author=obj).count()


class RequestSerializer(serializers.ModelSerializer):
    follow_requests = serializers.HyperlinkedRelatedField(read_only=True,
                                                          view_name='accounts:profile-detail',
                                                          lookup_field='uid',
                                                          lookup_url_kwarg='uid',
                                                          many=True)

    class Meta:
        model = Profile
        fields = ('follow_requests',)


class FollowersSerializer(serializers.ModelSerializer):
    profile_followers = serializers.HyperlinkedRelatedField(read_only=True,
                                                            view_name='accounts:profile-detail',
                                                            lookup_field='uid',
                                                            lookup_url_kwarg='uid',
                                                            many=True,
                                                            )

    class Meta:
        model = Profile
        fields = ('profile_followers',)


class FollowingsSerializer(serializers.ModelSerializer):
    profile_followings = serializers.HyperlinkedRelatedField(read_only=True,
                                                             view_name='accounts:profile-detail',
                                                             lookup_field='uid',
                                                             lookup_url_kwarg='uid',
                                                             many=True,
                                                             )

    class Meta:
        model = Profile
        fields = ('profile_followings',)


class BlockListSerializer(serializers.ModelSerializer):
    blocked_users = serializers.HyperlinkedRelatedField(read_only=True,
                                                        view_name='accounts:profile-detail',
                                                        lookup_field='uid',
                                                        lookup_url_kwarg='uid',
                                                        many=True,
                                                        )

    class Meta:
        model = Profile
        fields = ('blocked_users',)
