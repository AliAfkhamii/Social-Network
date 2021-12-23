from django.db import models

from django.utils.translation import gettext_lazy as _
from taggit.managers import TaggableManager
from django.utils import timezone

from accounts.models import Profile


class Post(models.Model):
    author = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='posts',
                               verbose_name=_('author'))
    title = models.CharField(max_length=256, verbose_name=_('title'))
    image = models.ImageField(blank=True, null=True, upload_to='post_images/', verbose_name=_('image'))
    file = models.FileField(blank=True, null=True, verbose_name=_('File'))
    slug = models.SlugField(max_length=100, null=True, blank=True, allow_unicode=True, verbose_name=_('slug'))
    content = models.TextField(verbose_name=_('content'))
    date_created = models.DateTimeField(auto_now_add=True, editable=False, verbose_name=_('date created'))
    date_edited = models.DateTimeField(auto_now=True, editable=False, verbose_name=_('date edited'))
    post_tags = TaggableManager(blank=True, verbose_name=_('post tags'))
    visits = models.ManyToManyField('IPAddress', related_name='posts_visited', verbose_name=_('views'),
                                    blank=True)

    class Meta:
        verbose_name = _('Post')
        verbose_name_plural = _('Posts')
        ordering = ('-date_created',)

    def __init__(self, *args, **kwargs):
        super(Post, self).__init__(*args, **kwargs)
        self.current_title = self.title

    def __str__(self):
        return f'{self.title}'

    def get_tags(self):
        return self.post_tags.names()

    def pinned_comments(self):
        return self.comments.filter(pinned=True)[:3]


class VoteManager(models.Manager):
    def total_stars_related_to_post(self, post):
        from functools import reduce
        from operator import add
        stars_list = self.filter(post=post).values_list('value', flat=True)
        if stars_list:
            total = reduce(add, stars_list)
            return total / len(stars_list)

        return 0


class Vote(models.Model):
    class StarChoices(models.IntegerChoices):
        VERY_BAD = 1, 'VERY_BAD'
        BAD = 2, 'BAD'
        OK = 3, 'OK'
        GOOD = 4, 'GOOD'
        PERFECT = 5, 'PERFECT'

    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='votes',
                             verbose_name=_('post'))

    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='votes_given',
                                verbose_name=_('profile voted'))

    created = models.DateTimeField(default=timezone.now, verbose_name=_('date created'))
    updated = models.DateTimeField(auto_now_add=True, verbose_name=_('date updated'))
    value = models.IntegerField(choices=StarChoices.choices, null=True, verbose_name=_('star'))
    objects = VoteManager()

    class Meta:
        verbose_name = _('Vote')
        verbose_name_plural = _('Votes')
        unique_together = (('post', 'profile'),)

    def __str__(self):
        return f"{self.profile} --> {self.post} | {self.value}"

    @classmethod
    def toggle(cls, post, profile, star=None):
        try:
            vote = cls.objects.get(post=post, profile=profile)
            if star:
                vote.value = star
                vote.save()
            else:
                vote.delete()
        except cls.DoesNotExist:
            obj = cls.objects.create(
                post=post, profile=profile, value=star
            )
            return obj

        return vote


class Comment(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.SET('from a deleted user'), verbose_name=_('user'))
    post = models.ForeignKey('Post', on_delete=models.CASCADE, related_name='comments', verbose_name=_('post'))
    text = models.TextField(null=True, verbose_name=_('text'))
    created = models.DateTimeField(auto_now_add=True, null=True, verbose_name=_('date created'))
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='replies',
                               verbose_name=_('replied to'))
    pinned = models.BooleanField(verbose_name=_('pinned'), default=False)

    @property
    def is_pinned(self):
        return self.pinned

    def __str__(self):
        if self.parent is not None:
            return f'{self.post}--{self.text[:10]}(reply)'

        return f'{self.post}--{self.text[:10]}'


class IPAddress(models.Model):
    ip = models.GenericIPAddressField(blank=True, null=True, verbose_name=_('ip address'))

    def __str__(self):
        return self.ip
