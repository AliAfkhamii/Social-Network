from rest_framework import serializers

from blog.models import Post
from .models import User, Profile, Relation


class UserOwnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = (
            "id",
            "password",
            "last_login",
            "is_superuser",
            "is_active",
            "is_staff",
            "groups",
            "user_permissions",
        )


class UserCreationSerializer(serializers.ModelSerializer):
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

    def validate_username(self, value):
        if not value:
            return self.context.get('request').user.username

        return value


class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    user = UserCreationSerializer(required=False)
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
            "phone": {'write_only': True}
        }

    def update(self, instance, validated_data):
        user_serializer = validated_data.pop("user", None)
        user = instance.user

        for field in user_serializer.keys():
            exec(f'user.{field} = user_serializer.get("{field}", instance.user.{field})')

        user.save(update_fields=[*user_serializer.keys()])

        return super(ProfileSerializer, self).update(instance, validated_data)

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
