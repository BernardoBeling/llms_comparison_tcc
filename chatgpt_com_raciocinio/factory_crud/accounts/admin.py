from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin
from django.core.exceptions import PermissionDenied
from .models import User


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    fieldsets = DjangoUserAdmin.fieldsets + (
        ("Dados adicionais", {"fields": ("name", "cnpj", "is_premium", "deleted_at")}),
    )
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (
        ("Dados adicionais", {"fields": ("name", "cnpj", "is_premium")}),
    )

    list_display = ("username", "email", "name", "is_premium", "is_staff", "is_active", "deleted_at")
    list_display_links = ("username", "email")
    search_fields = ("username", "email", "name", "cnpj")

    # Default: ninguém edita inline (vamos habilitar só para superuser dinamicamente)
    list_editable = ()

    def _can_edit_premium(self, request) -> bool:
        """
        ✅ Nova regra: qualquer superuser pode alterar is_premium no admin.
        """
        return bool(getattr(request.user, "is_superuser", False))

    def get_readonly_fields(self, request, obj=None):
        readonly = list(super().get_readonly_fields(request, obj))
        # ✅ Apenas superuser pode editar is_premium no formulário
        if not self._can_edit_premium(request):
            if "is_premium" not in readonly:
                readonly.append("is_premium")
        return readonly

    def save_model(self, request, obj, form, change):
        # ✅ Defesa: mesmo com POST manual, só superuser altera
        if change and "is_premium" in form.changed_data and not self._can_edit_premium(request):
            raise PermissionDenied("Apenas superusers podem alterar o status premium.")
        super().save_model(request, obj, form, change)

    def changelist_view(self, request, extra_context=None):
        """
        ✅ UX: na listagem de usuários, mostrar checkbox editável inline
        SOMENTE para superusers.
        """
        original_list_editable = getattr(self, "list_editable", ())
        original_list_display_links = getattr(self, "list_display_links", ("username", "email"))

        try:
            if self._can_edit_premium(request):
                # Permite editar inline na listagem (checkbox)
                self.list_editable = ("is_premium",)
                # is_premium não pode ser link se for editável
                self.list_display_links = ("username", "email")
            else:
                self.list_editable = ()
                self.list_display_links = ("username", "email")

            return super().changelist_view(request, extra_context=extra_context)
        finally:
            # Restaura para evitar efeitos colaterais
            self.list_editable = original_list_editable
            self.list_display_links = original_list_display_links
