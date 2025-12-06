from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from identity.models import User


# Кастомная админка для модели User
class UserAdmin(BaseUserAdmin):
    readonly_fields = ('id',)
    list_display = ('id', 'username', 'email', 'last_name')
    search_fields = ('username', 'last_name', 'email')
    fieldsets = (
        (None, {'fields': ('id', 'username', 'password')}),
        (_('Personal info'), {'fields': (
            'first_name', 'last_name', 'email', 'patronymic'
        )}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2'),
        }),
        (_('Personal info'), {'fields': (
            'first_name', 'last_name', 'email', 'patronymic'
        )}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser')
        })
    )


admin.site.register(User, UserAdmin)
