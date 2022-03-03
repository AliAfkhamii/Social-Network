from django.contrib import admin

from .models import (Post, Vote, Comment, )


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = list_filter = ('author', 'title',)


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    pass


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    pass
