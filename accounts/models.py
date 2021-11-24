from django.db import models
from django.utils.functional import lazy

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
        verbose_name = _('User')
        verbose_name_plural = _('Users')

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
    private = models.BooleanField(default=False)
    uid = models.UUIDField(default=uuid.uuid4, unique=True, blank=True, verbose_name=_('unique id'))

    def __str__(self):
        return f'{self.user} user profile'

    @property
    def votes(self):
        return self.votes_given.all()

    @property
    def is_private(self):
        return self.private

    def follow_requests(self):
        return self.followers.filter(state=Relation.RelationState.REQUESTED)

    def block_list(self):
        return self.followers.filter(state=Relation.RelationState.BLOCKED)

    def change_state(self):
        # profile_state_changed.send(sender=self.__class__, instance=self)
        self.private = not self.private
        self.save()

    class Meta:
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')


class Relation(models.Model):
    class RelationState(models.TextChoices):
        FOLLOWED = 'flw', 'followed'
        BLOCKED = 'blc', 'blocked'
        REQUESTED = 'req', 'requested'
        ACCEPTED = 'acc', 'accepted'

    follower = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='followings',
                                 verbose_name=_('follower'))

    account = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='followers',
                                verbose_name=_('account'))

    state = models.CharField(_('state'), max_length=3, null=True, choices=RelationState.choices)

    created = models.DateTimeField(auto_now_add=True, verbose_name=_('created'))

    def __str__(self):
        return f"{self.follower}-->{self.account} - {self.state}"

    def _terminate_relation(self):
        self.state = None  # or self.delete()

    def request(self):
        self.state = self.RelationState.REQUESTED
        self.save()

    def decline(self):
        self._terminate_relation()

    def accept(self):
        self.state = self.RelationState.ACCEPTED
        self.save()

    def follow(self):
        if self.state is None:
            self.state = self.RelationState.FOLLOWED

    def unfollow(self):
        self._terminate_relation()

    def block(self):
        self.state = self.RelationState.BLOCKED

    def unblock(self):
        self._terminate_relation()

    class Meta:
        verbose_name = _('Relation')
        verbose_name_plural = _('Relations')
        unique_together = (('follower', 'account'),)


class Link(models.Model):
    name = models.CharField(max_length=50, default='link', blank=True, verbose_name=_('link name'))
    url = models.URLField(verbose_name=_('url'))

    def __str__(self):
        return f"{self.name}"

    class Meta:
        verbose_name = _('Link')
        verbose_name_plural = _('Links')
