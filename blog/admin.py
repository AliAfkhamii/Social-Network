from django.contrib import admin

from .models import (Post, Vote, Comment, IPAddress)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    pass


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    pass


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass


@admin.register(IPAddress)
class IPAddressAdmin(admin.ModelAdmin):
    pass
