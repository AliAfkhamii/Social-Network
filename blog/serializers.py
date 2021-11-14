from rest_framework import serializers
from rest_framework.exceptions import ParseError

from .models import Post, Like, Comment
from accounts.models import Profile


class Tags(serializers.Field):
    def to_internal_value(self, data):
        return data

    def to_representation(self, value):
        return value


class PostSerializer(serializers.HyperlinkedModelSerializer):
    # author = serializers.ReadOnlyField(source='author.profile.uid')
    visits = serializers.SerializerMethodField(method_name='num_visits')
    likes = serializers.SerializerMethodField(method_name='num_likes')

    post_tags = Tags(source='get_tags', required=False)

    pinned_comments = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='blog:comment-detail-destroy'
    )

    class Meta:
        model = Post
        fields = (
            'url',
            # 'author',
            'title',
            'content',
            'image',
            'file',
            # 'slug',
            'visits',
            'likes',
            'post_tags',
            'date_created',
            'date_edited',
            'pinned_comments',
        )
        read_only_fields = ('slug', 'visits', 'likes', 'author',)
        optional_fields = ('image', 'file', 'post_tags',)
        extra_kwargs = {
            'url': {'view_name': 'blog:post-detail', 'lookup_field': 'slug'},
            # 'author': {'view_name': 'blog:post-detail', 'lookup_field': 'slug'}

        }

    def create(self, validated_data):
        tags = validated_data.pop('get_tags', None)
        instance = super(PostSerializer, self).create(validated_data)
        if tags is not None:
            instance.post_tags.add(tags)
        return instance

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


class CommentListSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.CharField(source='user.user.username', read_only=True)

    class Meta:
        model = Comment
        fields = (
            "url",
            "user",
            "post",
            "text",
            "created",
            "parent",
            "is_pinned"
        )
        # # extra_kwargs = {"parent": {"source": "parent.id"}}
        extra_kwargs = {
            'url': {'view_name': 'blog:comment-detail-destroy', 'lookup_field': 'pk'},
            'post': {'view_name': 'blog:post-detail', 'lookup_field': "slug"},
            'parent': {'view_name': 'blog:comment-detail-destroy', 'lookup_field': "pk"},
        }
        read_only_fields = ('parent', 'post',)


class CommentRetrieveSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.CharField(source='user.user.username', read_only=True)

    class Meta:
        model = Comment
        fields = (
            "user",
            "post",
            "text",
            "created",
            "parent",
            "replies",
            "is_pinned",
        )
        extra_kwargs = {
            'post': {'view_name': 'blog:post-detail', 'lookup_field': "slug"},
            'parent': {'view_name': 'blog:comment-detail-destroy', 'lookup_field': "pk"},
            'replies': {'view_name': 'blog:comment-detail-destroy', 'lookup_field': "pk"},
        }
        read_only_fields = (
            'post', 'created', 'parent', 'replies', 'is_pinned'
        )
