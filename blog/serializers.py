from rest_framework import serializers
from taggit_serializer.serializers import (TagListSerializerField,
                                           TaggitSerializer)

from accounts.models import Profile
from .models import Post, Vote, Comment
from .apps import BlogConfig as app
from accounts.apps import AccountsConfig as accounts_app


class PostSerializer(TaggitSerializer, serializers.HyperlinkedModelSerializer):
    stars = serializers.SerializerMethodField(method_name='votes')

    post_tags = TagListSerializerField(help_text="the format must be a \"list\" of tags")

    pinned_comments = serializers.HyperlinkedRelatedField(
        many=True,
        read_only=True,
        view_name='blog:comment-detail'
    )
    author_name = serializers.CharField(source='author.user.username', read_only=True)

    class Meta:
        model = Post
        fields = (
            'url',
            'author',
            'author_name',
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
            'url': {'view_name': f'{app.name}:post-detail', 'lookup_field': 'slug'},
            'author': {'view_name': f'{accounts_app.name}:profile-detail', 'lookup_field': 'uid'}
        }

    def votes(self, obj):
        return Vote.objects.total_stars_related_to_post(obj)


class VoteProfileSerializer(serializers.HyperlinkedModelSerializer):
    username = serializers.CharField(source='user.username')

    class Meta:
        model = Profile
        fields = ('username', 'url',)
        extra_kwargs = {"url": {"view_name": f"{accounts_app.name}:profile-detail", "lookup_field": "uid", }}


class VoteSerializer(serializers.HyperlinkedModelSerializer):
    profile = VoteProfileSerializer(read_only=True)
    value = serializers.ChoiceField(choices=Vote.StarChoices, required=False)
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
        extra_kwargs = {'post': {'view_name': f'{app.name}:post-detail', 'lookup_field': 'slug'}, }

    def create(self, validated_data):
        post = Post.objects.get(slug=self.context.get('view').kwargs.get('slug'))
        return Vote.toggle(
            post=post,
            profile=self.context.get('request').user.profile,
            star=self.validated_data.get('value')
        )


class CommentListSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.CharField(source='user.user.username', read_only=True)

    has_replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            "url",
            "user",
            "post",
            "text",
            "created",
            "parent",
            "parent_id",
            'has_replies',
            "is_pinned"
        )
        extra_kwargs = {
            'url': {'view_name': f'{app.name}:comment-detail', 'lookup_field': 'pk'},
            'post': {'view_name': f'{app.name}:post-detail', 'lookup_field': "slug"},
            'parent': {'view_name': f'{app.name}:comment-detail', 'lookup_field': "pk"},
        }
        read_only_fields = ('parent', 'post', 'parent_id')

    def get_has_replies(self, obj):
        return obj.replies.all().exists()


class CommentRetrieveSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.CharField(source='user.user.username', read_only=True)

    has_replies = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = (
            "url",
            "user",
            "post",
            "text",
            "created",
            "parent",
            'has_replies',
            "is_pinned",
        )
        extra_kwargs = {
            'url': {'view_name': f'{app.name}:comment-detail', 'lookup_field': 'pk'},
            'post': {'view_name': f'{app.name}:post-detail', 'lookup_field': "slug"},
            'parent': {'view_name': f'{app.name}:comment-detail', 'lookup_field': "pk"},
        }
        read_only_fields = (
            'post', 'created', 'parent', 'is_pinned'
        )

    def get_has_replies(self, obj):
        return obj.replies.all().exists()
