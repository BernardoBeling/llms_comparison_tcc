from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Machine, Production, ProductionMachine

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Informações Adicionais', {'fields': ('name', 'cnpj', 'is_premium')}),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return self.readonly_fields + ('is_premium',)
        return self.readonly_fields

admin.site.register(User, CustomUserAdmin)
admin.site.register(Machine)
admin.site.register(Production)
admin.site.register(ProductionMachine)
