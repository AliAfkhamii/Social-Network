from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, Profile
from .forms import *


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
    pass