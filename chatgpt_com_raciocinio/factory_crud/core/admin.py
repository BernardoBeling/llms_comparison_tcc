from django.contrib import admin
from .models import Machine, Production, ProductionMachine


class ProductionMachineInline(admin.TabularInline):
    model = ProductionMachine
    extra = 0
    autocomplete_fields = ["machine"]
    fields = ("machine", "status", "started_at", "finished_at", "canceled_at", "working_time")
    readonly_fields = ("working_time",)


@admin.register(Machine)
class MachineAdmin(admin.ModelAdmin):
    list_display = ("id", "model", "serialnumber", "owner_user", "created_at", "deleted_at")
    search_fields = ("model", "serialnumber", "owner_user__username", "owner_user__email")
    list_filter = ("deleted_at",)


@admin.register(Production)
class ProductionAdmin(admin.ModelAdmin):
    list_display = ("id", "description", "quantity", "user", "status", "started_at", "finished_at", "canceled_at", "created_at")
    search_fields = ("description", "user__username", "user__email")
    list_filter = ("status", "deleted_at")
    inlines = [ProductionMachineInline]


@admin.register(ProductionMachine)
class ProductionMachineAdmin(admin.ModelAdmin):
    list_display = ("id", "production", "machine", "status", "working_time", "started_at", "finished_at", "canceled_at", "created_at")
    list_filter = ("status", "deleted_at")
    search_fields = ("production__description", "machine__serialnumber", "machine__model")
    readonly_fields = ("working_time",)
