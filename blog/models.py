from django.db import models

from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager
import uuid
from django.utils import timezone
from django.conf import settings

from . import utils


class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='posts',
                               verbose_name=_('author'))
    title = models.CharField(max_length=256, verbose_name=_('title'))
    image = models.ImageField(blank=True, null=True, upload_to='post_images/', verbose_name=_('image'))
    file = models.FileField(blank=True, null=True, verbose_name=_('File'))
    slug = models.SlugField(null=True, blank=True, allow_unicode=True, verbose_name=_('slug'))
    content = models.TextField(verbose_name=_('content'))
    date_created = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=_('date created'))
    date_edited = models.DateTimeField(auto_now=True, editable=False, verbose_name=_('date edited'))
    post_tags = TaggableManager(blank=True, verbose_name=_('post tags'))
    visits = models.ManyToManyField('IPAddress', related_name='posts_visited', verbose_name=_('views'),
                                    blank=True)

    # def __init__(self, *args, **kwargs):
    #     self.current_slug = self.slug if self.slug else None
    #     super(Post, self).__init__(*args, **kwargs)

    class Meta:
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')
        ordering = ('-date_created',)

    def get_tags(self):
        return self.post_tags.names()

    def save(self, *args, **kwargs):
        if not self.slug:
            # get the field we want to slugify based on that
            indicator = self.title if self.title else (self.title, self.author)
            exists, to_slug = utils.get_slug(self, indicator)
            while exists:
                exists, to_slug = utils.get_slug(self, indicator, uuid.uuid4())
            self.slug = self.current_slug = to_slug
            self.save()
        super().save(*args, *kwargs)

    # def toggle_like(self, request):
    #     from .signals import post_like
    #
    #     profile = request.user.profile
    #     is_liked = not self.is_liked(profile)
    #
    #     if is_liked:
    #         self._like(request)
    #     else:
    #         self._unlike()
    #
    #     self.refresh_from_db()
    #     post_like.send(sender=self.__class__, instance=self, profile=profile, state=is_liked)

    # def _like(self, request):
    #     self.likes_count = F('likes_count') + 1
    #     self.like_timestamp = str(datetime.now(tz=timezone.utc)) + str(request.user)
    #     self.save()

    # def _unlike(self):
    #     self.likes_count = F('likes_count') - 1
    #     # del self.like_timestamp
    #     self.save()

    def __str__(self):
        return f'{self.title}'


class LikeManager(models.Manager):
    def total_star_related_to_post(self, post_id):
        from functools import reduce
        from operator import add
        related_post = Post.objects.get(id=post_id)
        stars_list = self.filter(post=related_post).values_list('value', flat=True)
        total = reduce(add, stars_list)
        return total


class Like(models.Model):
    class StarChoices(models.IntegerChoices):
        VERY_BAD = 1, 'VERY_BAD'
        BAD = 2, 'BAD'
        OK = 3, 'OK'
        GOOD = 4, 'GOOD'
        PERFECT = 5, 'PERFECT'

    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='likes',
                             verbose_name=_('post'))

    profile = models.ForeignKey('accounts.Profile', on_delete=models.CASCADE, related_name='likes_given',
                                verbose_name=_('profile liked'))

    created = models.DateTimeField(default=timezone.now, verbose_name=_('date created'))
    value = models.IntegerField(choices=StarChoices.choices, null=True, verbose_name=_('star'))
    objects = LikeManager()

    class Meta:
        verbose_name = _('Like')
        verbose_name_plural = _('Likes')
        unique_together = (('post', 'profile'),)

    def __str__(self):
        return f"{self.profile} --> {self.post} | {self.value}"

    @classmethod
    def toggle(cls, post, profile, star=None):
        try:
            like = cls.objects.get(post=post, profile=profile)
            if star:
                like.value = star
                like.save()
            else:
                like.delete()
        except Like.DoesNotExist:
            obj = cls.objects.create(
                post=post, profile=profile, value=star
            )
            return obj


class Comment(models.Model):
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments', verbose_name=_('post'))
    text = models.TextField(null=True, verbose_name=_('text'))
    created = models.DateTimeField(auto_now_add=True, null=True, verbose_name=_('date created'))
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies',
                               verbose_name=_('replied to'))

    def __str__(self):
        if self.parent:
            return f'{self.parent} --- {self.text[:20]}'

        return f'{self.post}-{self.text[:20]}'


class IPAddress(models.Model):
    ip = models.GenericIPAddressField(blank=True, null=True, verbose_name=_('ip address'))

    def __str__(self):
        return self.ip
