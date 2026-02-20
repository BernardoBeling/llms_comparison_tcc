from django import forms
from django.core.exceptions import ValidationError
from django.db import transaction
from .models import Machine, Production, ProductionMachine, ProductionStatus, ProductionMachineStatus
from .services import get_available_machines_for_user


class MachineForm(forms.ModelForm):
    class Meta:
        model = Machine
        fields = ["model", "serialnumber"]

    def __init__(self, *args, **kwargs):
        self.owner_user = kwargs.pop("owner_user", None)
        super().__init__(*args, **kwargs)

    def clean_serialnumber(self):
        serial = self.cleaned_data.get("serialnumber", "").strip()
        if not serial:
            raise ValidationError("Serialnumber é obrigatório.")
        return serial

    def clean(self):
        cleaned = super().clean()
        if self.owner_user is None:
            raise ValidationError("Usuário proprietário não informado.")

        # ✅ Incremental: limite por tipo de usuário
        limit = 10 if getattr(self.owner_user, "is_premium", False) else 5

        user_machine_count = Machine.objects.filter(owner_user=self.owner_user).count()
        if self.instance.pk is None and user_machine_count >= limit:
            raise ValidationError(f"Cada usuário pode cadastrar no máximo {limit} máquinas.")
        return cleaned

    def save(self, commit=True):
        obj = super().save(commit=False)
        obj.owner_user = self.owner_user
        if commit:
            obj.save()
        return obj


class ProductionCreateForm(forms.ModelForm):
    machines = forms.ModelMultipleChoiceField(
        queryset=Machine.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label="Máquinas",
    )

    class Meta:
        model = Production
        fields = ["description", "quantity", "machines"]

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop("user", None)
        super().__init__(*args, **kwargs)

        if self.user is not None:
            self.fields["machines"].queryset = get_available_machines_for_user(self.user)

    def clean(self):
        cleaned = super().clean()
        if self.user is None:
            raise ValidationError("Usuário não informado.")
        machines = cleaned.get("machines")
        if not machines or machines.count() == 0:
            raise ValidationError("Não é permitido cadastrar uma produção sem máquinas associadas.")
        return cleaned

    @transaction.atomic
    def save(self, commit=True):
        production = super().save(commit=False)
        production.user = self.user
        production.status = ProductionStatus.STANDBY

        if commit:
            production.save()

        machines = self.cleaned_data["machines"]
        for m in machines:
            ProductionMachine.objects.create(
                production=production,
                machine=m,
                status=ProductionMachineStatus.STANDBY,
            )

        return production
