from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Machine, Production, ProductionMachine

class CustomUserAdmin(UserAdmin):
    # Requisito 1.3 e 1.4
    fieldsets = UserAdmin.fieldsets + (
        ('Status Premium', {'fields': ('is_premium',)}),
    )
    
    def get_readonly_fields(self, request, obj=None):
        if not request.user.is_superuser:
            return ('is_premium',)
        return super().get_readonly_fields(request, obj)

admin.site.register(User, CustomUserAdmin)
admin.site.register(Machine)
admin.site.register(Production)
admin.site.register(ProductionMachine)