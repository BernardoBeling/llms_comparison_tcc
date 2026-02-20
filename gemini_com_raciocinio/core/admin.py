from django.contrib import admin
from .models import User, Machine, Production, ProductionMachine

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'is_premium', 'is_superuser')
    search_fields = ('email', 'name')
    
    def get_readonly_fields(self, request, obj=None):
        # Req 1.4: Apenas o superusuário real pode alterar o status premium
        if not request.user.is_superuser:
            return ('is_premium',)
        return ()

admin.site.register(Machine)
admin.site.register(Production)
admin.site.register(ProductionMachine)