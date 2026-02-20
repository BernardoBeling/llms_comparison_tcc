from django.contrib import admin
from django.core.exceptions import PermissionDenied
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .admin_forms import UserAdminChangeForm, UserAdminCreationForm
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
	add_form = UserAdminCreationForm
	form = UserAdminChangeForm
	model = User

	list_display = ('id', 'name', 'email', 'cnpj', 'is_premium', 'is_staff', 'is_active', 'created_at')
	list_filter = ('is_staff', 'is_active')
	search_fields = ('name', 'email', 'cnpj')
	ordering = ('id',)

	fieldsets = (
		(None, {'fields': ('name', 'password')}),
		('Informações', {'fields': ('email', 'cnpj', 'is_premium')}),
		('Permissões', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
		('Datas', {'fields': ('last_login', 'date_joined', 'created_at', 'updated_at', 'deleted_at')}),
	)

	add_fieldsets = (
		(
			None,
			{
				'classes': ('wide',),
				'fields': (
					'name',
					'email',
					'cnpj',
					'password1',
					'password2',
					'is_premium',
					'is_staff',
					'is_superuser',
					'is_active',
				),
			},
		),
	)

	readonly_fields = ('created_at', 'updated_at', 'deleted_at', 'date_joined', 'last_login')
	filter_horizontal = ('groups', 'user_permissions')

	def get_readonly_fields(self, request, obj=None):
		readonly = list(super().get_readonly_fields(request, obj=obj))
		if request.user.is_authenticated and getattr(request.user, 'name', None) != 'admin':
			readonly.append('is_premium')
		return tuple(readonly)

	def save_model(self, request, obj, form, change):
		if change and 'is_premium' in getattr(form, 'changed_data', []):
			if not (request.user.is_authenticated and getattr(request.user, 'name', None) == 'admin'):
				raise PermissionDenied('Apenas o usuário "admin" pode alterar o status premium.')
		return super().save_model(request, obj, form, change)
