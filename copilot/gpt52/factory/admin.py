from django.contrib import admin

from .models import Machine, Production, ProductionMachine


@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
	list_display = ('id', 'model', 'serialnumber', 'owner', 'created_at', 'deleted_at')
	search_fields = ('model', 'serialnumber', 'owner__name')
	list_filter = ('deleted_at',)


@admin.register(Production)
class ProductionAdmin(admin.ModelAdmin):
	list_display = ('id', 'description', 'user', 'status', 'created_at', 'deleted_at')
	search_fields = ('description', 'user__name')
	list_filter = ('status', 'deleted_at')


@admin.register(ProductionMachine)
class ProductionMachineAdmin(admin.ModelAdmin):
	list_display = ('id', 'production', 'machine', 'status', 'created_at', 'deleted_at')
	list_filter = ('status', 'deleted_at')

# Register your models here.
