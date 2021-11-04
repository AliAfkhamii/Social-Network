from django.db import models
from django.utils.functional import lazy

from django.utils.translation import gettext_lazy as _


class Relation(models.Model):
    class RelType(models.TextChoices):
        PUBLIC = 'PUBLIC', 'Public'
        PRIVATE = 'PRIVATE', 'Private'

    follower = models.ForeignKey('profile', on_delete=models.CASCADE, related_name='followings',
                                 verbose_name=_('follower'))

    account = models.ForeignKey('accounts.Profile', on_delete=models.CASCADE, related_name='followers',
                                verbose_name=_('following'))

    state = models.CharField(_('state'), max_length=3, null=True)

    created = models.DateTimeField(auto_now_add=True, verbose_name=_('created'))

    types = models.CharField(max_length=7, choices=RelType.choices, default=RelType.PUBLIC,
                             verbose_name=_('type'))

    def __str__(self):
        return f"{self.follower}-->{self.account}"

    def save(self, *args, **kwargs):
        if self.account.is_private:
            self.types = self.RelType.PRIVATE
        else:
            self.types = self.RelType.PUBLIC
        super(Relation, self).save(*args, **kwargs)

    def _terminate_relation(self):
        self.state = None  # or self.delete()
        self.save()

    def unblock(self):
        self._terminate_relation()

    class Meta:
        verbose_name = _('Relation')
        verbose_name_plural = _('Relations')
        unique_together = (('follower', 'account'),)


class PublicRelManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super(PublicRelManager, self).get_queryset(*args, **kwargs).filter(types=self.RelType.PUBLIC)


class PublicRelation(Relation):
    class RelationStates(models.TextChoices):
        FOLLOWED = 'FLW', 'followed'
        BLOCKED = 'BLC', 'blocked'

    objects = PublicRelManager()

    def __init__(self, *args, **kwargs):
        super(PublicRelation, self).__init__(*args, **kwargs)
        self._meta.get_field('state').choices = lazy(self.RelationStates.choices, list)()

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.types = self.RelType.PUBLIC
        super(PublicRelation, self).save(*args, **kwargs)

    def follow(self):
        if self.state is None:
            self.state = self.RelationStates.FOLLOWED
            self.save()

    def unfollow(self):
        self._terminate_relation()

    def block(self):
        self.state = self.RelationStates.BLOCKED
        self.save()

    def change_state(self):
        self.types = self.RelType.PRIVATE
        self.save()

    class Meta:
        verbose_name = _('public relationship')
        verbose_name_plural = _('public relationships')
        proxy = True


class PrivateRelManager(models.Manager):
    def get_queryset(self, *args, **kwargs):
        return super(PrivateRelManager, self).get_queryset(*args, **kwargs).filter(types=self.RelType.PRIVATE)


class PrivateRelation(Relation):
    class RelationStates(models.TextChoices):
        REQUESTED = 'REQ', 'requested'
        ACCEPTED = 'ACC', 'accepted'
        BLOCKED = 'BLC', 'blocked'

    objects = PrivateRelManager()

    def __init__(self, *args, **kwargs):
        super(PrivateRelation, self).__init__(*args, **kwargs)
        self._meta.get_field('state').choices = lazy(self.RelationStates.choices, list)()

    def save(self, *args, **kwargs):
        if self.pk is None:
            self.types = self.RelType.PRIVATE
        super(PrivateRelation, self).save(*args, **kwargs)

    def request(self):
        self.state = self.RelationStates.REQUESTED
        self.save()

    def accept(self):
        self.state = self.RelationStates.ACCEPTED
        self.save()

    def decline(self):
        self._terminate_relation()

    def block(self):
        self.state = self.RelationStates.BLOCKED

    def change_state(self):
        self.types = self.RelType.PUBLIC
        self.save()

    class Meta:
        verbose_name = _('private relationship')
        verbose_name_plural = _('private relationships')
        proxy = True
