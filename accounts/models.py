from django.db import models

from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator

import uuid


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, username, password=None, **extra_fields):
        if not email:
            raise ValueError(_('user must have an email'))
        if not username:
            raise ValueError(_('username is required'))
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, password=password, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)

        return self._create_user(email=email, username=username, password=password, **extra_fields)

    def create_superuser(self, email, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email=email, username=username, password=password, **extra_fields)


class UserModel(PermissionsMixin, AbstractBaseUser):
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _('username'),
        max_length=150,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=(username_validator,),
        error_messages={
        },
    )
    phone = models.CharField(max_length=100, blank=True, null=True)
    email = models.EmailField(unique=True, verbose_name=_('Email Address'))
    is_active = models.BooleanField(default=True, verbose_name=_('active'))
    is_staff = models.BooleanField(default=False, verbose_name=_('staff status'))
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name=_('date_joined'))
    first_name = models.CharField(max_length=150, blank=True, verbose_name=_('first name'))
    last_name = models.CharField(max_length=150, blank=True, verbose_name=_('last name'))

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username',)

    class Meta:
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    def __str__(self):
        return self.username

    @property
    def is_admin(self):
        return self.is_staff


User = get_user_model()


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    picture = models.ImageField(default="default.png", upload_to='profile_pictures/', blank=True,
                                verbose_name=_('profile picture'))

    bio = models.CharField(max_length=100, default="", blank=True, verbose_name=_('bio'))

    links = models.ManyToManyField('Link', related_name='profiles', blank=True,
                                   verbose_name=_('links'))

    uid = models.UUIDField(default=uuid.uuid4, unique=True, blank=True, verbose_name=_('unique id'))

    def __str__(self):
        return f'{self.user} user profile'

    @property
    def likes(self):
        return self.likes_given

    # @property
    # def followers(self):
    #     return self.followers
    #
    # @property
    # def followings(self):
    #     return self.followings

    def follow_requests(self):
        relations = self.followers
        return relations.filter(state=relations.FollowState.REQUESTED)


class Relation(models.Model):
    class FollowState(models.TextChoices):
        REQUESTED = 'r', 'requested'
        ACCEPTED = 'a', 'accepted'
        DECLINED = 'd', 'declined'

    follower = models.ForeignKey('profile', on_delete=models.CASCADE, related_name='followings',
                                 verbose_name=_('follower'))
    account = models.ForeignKey('profile', on_delete=models.CASCADE, related_name='followers',
                                verbose_name=_('following'))

    state = models.CharField(max_length=9, choices=FollowState.choices, null=True, verbose_name=_('state'))

    created = models.DateTimeField(auto_now_add=True, verbose_name=_('created'))

    class Meta:
        verbose_name = _('Relation')
        verbose_name_plural = _('Relations')
        unique_together = (('follower', 'account'),)

    def __str__(self):
        return f"{self.follower}-->{self.account}"

    def _request(self):
        self.state = self.FollowState.REQUESTED
        self.save()

    def _accept(self):
        self.state = self.FollowState.ACCEPTED
        self.save()

    def decline(self):
        self.state = self.FollowState.DECLINED
        self.save()

    def follow(self):

        if self.state == self.FollowState.REQUESTED:
            self._accept()

        elif self.state != self.FollowState.ACCEPTED:
            self._request()

    def unfollow(self):
        self.state = None
        self.save()


class Link(models.Model):
    name = models.CharField(max_length=50, default='link', blank=True, verbose_name=_('link name'))
    url = models.URLField(verbose_name=_('url'))

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Link')
        verbose_name_plural = _('Links')