from rest_framework import serializers
from rest_framework.exceptions import ParseError

from .models import Post, Like
from accounts.models import Profile


class Tags(serializers.Field):
    def to_internal_value(self, data):
        return data

    def to_representation(self, value):
        return value


class PostSerializer(serializers.ModelSerializer):
    author = serializers.ReadOnlyField(source='author.profile.uid')
    visits = serializers.SerializerMethodField(method_name='num_visits')
    likes = serializers.SerializerMethodField(method_name='num_likes')
    post_tags = Tags(source='get_tags')

    class Meta:
        model = Post
        fields = (
            'id',
            'author_id',
            'author',
            'title',
            'content',
            'image',
            'file',
            'slug',
            'visits',
            'likes',
            'post_tags',
            'date_created',
            'date_edited',
        )
        read_only_fields = ('slug', 'visits', 'likes',)
        optional_fields = ('image', 'file', 'post_tags',)

    def create(self, validated_data):
        tags = validated_data.pop('get_tags', None)
        instance = Post.objects.create(**validated_data)
        if tags is not None:
            instance.post_tags.add(tags)
        return instance

    def update(self, instance, validated_data):
        return super(PostSerializer, self).update(instance, validated_data)

    def num_visits(self, obj):
        return obj.visits.count()

    def num_likes(self, obj):
        return obj.likes.count()


class ProfileLikeSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.username')

    class Meta:
        model = Profile
        fields = (
            'id',
            'user',
            'picture',
            'bio',
        )


class LikeSerializer(serializers.ModelSerializer):
    profile = ProfileLikeSerializer(required=False)
    value = serializers.ChoiceField(choices=Like.StarChoices)

    class Meta:
        model = Like
        fields = (
            'id',
            'post',
            'profile',
            'created',
            'value',
        )
        read_only_fields = ('created',)
