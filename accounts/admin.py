from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.utils.translation import gettext_lazy as _

from django.contrib.auth import get_user_model
from .models import Profile, Relation
from .forms import *

User = get_user_model()


@admin.register(User)
class UserAdmin(DefaultUserAdmin):
    form = AdministrationUserChangeForm
    add_form = UserRegistrationForm
    fieldsets = (
        (None, {'fields': ('email', 'password', 'username')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {'fields': ('email', 'username', 'password', 'password2'), }),
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('id',
                    'user',
                    'email',
                    'uid',
                    'website',
                    'private',
                    )

    list_display_links = ('id',
                          'user',
                          'email',
                          'uid',
                          'website',
                          )

    def email(self, obj):
        return obj.user.email


@admin.register(Relation)
class RelationAdmin(admin.ModelAdmin):
    list_display = (
        "actor", "account", "state"
    )

    list_display_links = (
        "actor", "account"
    )

    list_editable = ('state',)
