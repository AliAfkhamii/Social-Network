from django.apps import apps
from django.db import models

from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.contrib.auth.validators import UnicodeUsernameValidator

import uuid


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, email, username, password, **extra_fields):
        if not email:
            raise ValueError(_('user must have an email'))
        if not username:
            raise ValueError(_('username is required'))

        GlobalUserModel = apps.get_model(self.model._meta.app_label, self.model._meta.object_name)
        username = GlobalUserModel.normalize_username(username)
        email = self.normalize_email(email)
        user = self.model(email=email, username=username, **extra_fields)
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
    picture = models.ImageField(default="profile_pictures/default.jpg", upload_to='profile_pictures/', blank=True,
                                verbose_name=_('profile picture'))

    bio = models.CharField(max_length=100, default="", blank=True, verbose_name=_('bio'))

    website = models.URLField(verbose_name=_('Website'), default='', blank=True)
    private = models.BooleanField(default=False)
    uid = models.UUIDField(default=uuid.uuid4, unique=True, blank=True, verbose_name=_('unique id'))

    def __str__(self):
        return f'{self.user}'

    @property
    def votes(self):
        return self.votes_given.all()

    @property
    def is_private(self):
        return self.private

    def follow_requests(self):
        pks = self.followers.filter(state=Relation.RelationState.REQUESTED).values_list('actor', flat=True)
        return self.__class__.objects.filter(pk__in=pks)

    def profile_followers(self):
        pks = self.followers.filter(state=Relation.RelationState.FOLLOWED).values_list('actor', flat=True)
        return self.__class__.objects.filter(pk__in=pks)

    def profile_followings(self):
        pks = self.followings.filter(state=Relation.RelationState.FOLLOWED).values_list('account', flat=True)
        return self.__class__.objects.filter(pk__in=pks)

    def block_list(self):
        return self.followings.filter(state=Relation.RelationState.BLOCKED).values_list('account', flat=True)

    def blocked_users(self):
        return self.__class__.objects.filter(pk__in=self.block_list())

    def change_state(self):
        from accounts.signals import profile_state_changed
        if self.is_private:
            profile_state_changed.send(sender=self.__class__, instance=self)

        self.private = not self.private
        self.save()

    class Meta:
        verbose_name = _('Profile')
        verbose_name_plural = _('Profiles')


class Relation(models.Model):
    class RelationState(models.TextChoices):
        FOLLOWED = 'FLW', 'FOLLOWED'
        BLOCKED = 'BLC', 'BLOCKED'
        REQUESTED = 'REQ', 'REQUESTED'

    actor = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='followings',
                              verbose_name=_('actor'))

    account = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='followers',
                                verbose_name=_('account'))

    state = models.CharField(_('state'), max_length=3, choices=RelationState.choices)

    created = models.DateTimeField(auto_now_add=True, verbose_name=_('created'))

    def __str__(self):
        return f"{self.state}"

    def _terminate_relation(self):
        self.delete()

    def _request(self):
        self.state = self.RelationState.REQUESTED
        self.save()

    def decline(self):
        self._terminate_relation()
        return f"{self.actor}'s request declined"

    def accept(self):
        self.state = self.RelationState.FOLLOWED
        self.save()
        return f"{self.actor}'s request accepted"

    def follow(self):
        if self.account.is_private:
            self._request()
            return f"request sent to {self.account}"
        else:
            self.state = self.RelationState.FOLLOWED
            self.save()
            return f"{self.account} followed"

    def unfollow(self):
        self._terminate_relation()
        return f"{self.account} unfollowed"

    def block(self):
        from .signals import profile_blocked
        self.state = self.RelationState.BLOCKED
        self.save()
        profile_blocked.send(sender=self.__class__, instance=self)
        return f"{self.account} blocked"

    def unblock(self):
        self._terminate_relation()
        return f"{self.account} unblocked"

    def undo_req(self):
        self._terminate_relation()
        return f"follow request to {self.account} is undone"

    class Meta:
        verbose_name = _('Relation')
        verbose_name_plural = _('Relations')
        unique_together = (('actor', 'account'),)
