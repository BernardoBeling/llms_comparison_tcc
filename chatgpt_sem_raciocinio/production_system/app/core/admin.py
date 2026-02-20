from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


# @admin.register(User)
# class CustomUserAdmin(UserAdmin):
#     fieldsets = UserAdmin.fieldsets + (
#         ('Premium', {'fields': ('is_premium',)}),
#     )

#     def get_readonly_fields(self, request, obj=None):
#         if not request.user.username == 'admin':
#             return ('is_premium',)
#         return ()

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'username',
        'email',
        'is_premium',
        'is_staff',
        'is_superuser'
    )

    list_filter = ('is_premium', 'is_staff', 'is_superuser')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Informações Pessoais', {'fields': ('name', 'email', 'cnpj')}),
        ('Plano', {'fields': ('is_premium',)}),
        ('Permissões', {
            'fields': (
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            )
        }),
        ('Datas importantes', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'username',
                'email',
                'name',
                'cnpj',
                'password1',
                'password2',
                'is_premium',
            ),
        }),
    )

    search_fields = ('username', 'email', 'cnpj')
    ordering = ('username',)