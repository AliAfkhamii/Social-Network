from rest_framework import serializers
from taggit_serializer.serializers import (TagListSerializerField,
                                           TaggitSerializer)

from .models import Post, Vote, Comment
from accounts.models import Profile


class PostSerializer(TaggitSerializer, serializers.HyperlinkedModelSerializer):
    author = serializers.ReadOnlyField(source='author.user.username')
    visits = serializers.SerializerMethodField(method_name='num_visits')
    stars = serializers.SerializerMethodField(method_name='votes')

    post_tags = TagListSerializerField(help_text="the format must be a \"list\" of tags")

    pinned_comments = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='blog:comment-detail'
    )

    class Meta:
        model = Post
        fields = (
            'url',
            'author',
            'title',
            'content',
            'image',
            'file',
            # 'slug',
            'visits',
            'stars',
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

    def num_visits(self, obj):
        return obj.visits.count()

    def votes(self, obj):
        return Vote.objects.total_stars_related_to_post(obj)


class ProfileLikeSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username')

    class Meta:
        model = Profile
        fields = (
            'username',
            'picture',
            'bio',
        )


class VoteSerializer(serializers.HyperlinkedModelSerializer):
    profile = ProfileLikeSerializer(read_only=True)
    value = serializers.ChoiceField(choices=Vote.StarChoices)
    url = serializers.HyperlinkedIdentityField(view_name='blog:vote-detail')

    class Meta:
        model = Vote
        fields = (
            'url',
            'post',
            'profile',
            'created',
            'updated',
            'value',
        )
        read_only_fields = ('created', 'updated', 'post', 'profile')
        extra_kwargs = {'post': {'view_name': 'blog:post-detail', 'lookup_field': 'slug'}, }


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
        extra_kwargs = {
            'url': {'view_name': 'blog:comment-detail', 'lookup_field': 'pk'},
            'post': {'view_name': 'blog:post-detail', 'lookup_field': "slug"},
            'parent': {'view_name': 'blog:comment-detail', 'lookup_field': "pk"},
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
            'parent': {'view_name': 'blog:comment-detail', 'lookup_field': "pk"},
            'replies': {'view_name': 'blog:comment-detail', 'lookup_field': "pk"},
        }
        read_only_fields = (
            'post', 'created', 'parent', 'replies', 'is_pinned'
        )
