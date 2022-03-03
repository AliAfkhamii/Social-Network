from django.contrib import admin

from .models import ObjectLog


@admin.register(ObjectLog)
class ObjectLogAdmin(admin.ModelAdmin):
    list_display = ('user', 'ip', 'content_type', 'timestamp',)
    list_filter = ('user', 'ip', 'content_type', 'timestamp',)
