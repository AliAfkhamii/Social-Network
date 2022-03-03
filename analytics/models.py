from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils.translation import gettext_lazy as _
from django.db import models

from accounts.models import User


class ObjectLog(models.Model):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, null=True, related_name='logs')
    ip = models.GenericIPAddressField(verbose_name=_('IPAddress'))
    content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING, verbose_name=_('Content Type'))
    object_id = models.PositiveBigIntegerField(verbose_name=_('Object id'))
    content_object = GenericForeignKey('content_type', 'object_id')
    timestamp = models.DateTimeField(auto_now=True, verbose_name=_('Timestamp'))

    def __str__(self):
        return f'{self.content_object} | {self.timestamp}'

    class Meta:
        ordering = ('-timestamp',)
        verbose_name = _('Object Logger')
        verbose_name_plural = _('Objects Logger')


class IPAddress(models.Model):
    ip = models.GenericIPAddressField(blank=True, null=True, verbose_name=_('ip address'))

    def __str__(self):
        return self.ip


LOGGER_MODEL = getattr('settings', 'LOGGER_MODEL', ObjectLog)
