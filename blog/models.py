from django.db import models

from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager
import uuid
from django.utils import timezone
from django.conf import settings

from .utils import get_slug


class Post(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, related_name='posts',
                               verbose_name=_('author'))
    title = models.CharField(max_length=256, blank=True, verbose_name=_('title'))
    image = models.ImageField(blank=True, upload_to='post_images/', verbose_name=_('image'))
    file = models.FileField(blank=True, verbose_name=_('File'))
    slug = models.SlugField(null=True, blank=True, allow_unicode=True, verbose_name=_('slug'))
    content = models.TextField(verbose_name=_('content'))
    date_created = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=_('date created'))
    date_edited = models.DateTimeField(auto_now=True, editable=False, verbose_name=_('date edited'))
    post_tags = TaggableManager(blank=True, verbose_name=_('post tags'))
    visits = models.ManyToManyField('IPAddress', related_name='posts_visited', verbose_name=_('views'))

    class Meta:
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')
        ordering = ('-date_created',)

    @property
    def likes(self):
        return self.likes.all()

    def save(self, *args, **kwargs):
        if not self.slug:
            if self.title:
                exists, to_slug = get_slug(self, self.title)
                while exists:
                    exists, to_slug = get_slug(self, self.title, uuid.uuid4())
            else:
                exists, to_slug = get_slug(self, self.author, uuid.uuid4())
                while exists:
                    exists, to_slug = get_slug(self, self.author, uuid.uuid4())
            self.slug = to_slug
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
    pass


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
    value = models.IntegerField(choices=StarChoices.choices, blank=True, null=True, verbose_name=_('star'))
    objects = LikeManager()

    class Meta:
        verbose_name = _('Like')
        verbose_name_plural = _('Likes')
        unique_together = (('post', 'profile'),)

    @classmethod
    def toggle_like(cls, post, profile, star=None):
        try:
            like = cls.objects.get(post=post, profile=profile)
            if star:
                like.value = star
                like.save()
            else:
                like.delete()
        except Like.DoesNotExist:
            cls.objects.create(
                post=post, profile=profile, value=star
            )


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
