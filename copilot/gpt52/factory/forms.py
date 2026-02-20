from __future__ import annotations

from django import forms
from .models import (
    Machine,
    Production,
    ProductionMachine,
    ProductionMachineStatus,
    ProductionStatus,
)


class MachineForm(forms.ModelForm):
    class Meta:
        model = Machine
        fields = ('model', 'serialnumber')

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean_serialnumber(self):
        value = (self.cleaned_data.get('serialnumber') or '').strip()
        if not value:
            raise forms.ValidationError('Serial number é obrigatório')
        return value

    def clean(self):
        cleaned = super().clean()
        if self.user is None:
            return cleaned

        max_machines = 10 if getattr(self.user, 'is_premium', False) else 5
        if Machine.objects.filter(owner=self.user).count() >= max_machines:
            raise forms.ValidationError(f'Cada usuário pode cadastrar no máximo {max_machines} máquinas.')
        return cleaned

    def save(self, commit=True):
        instance: Machine = super().save(commit=False)
        instance.owner = self.user
        if commit:
            instance.save()
        return instance


class ProductionForm(forms.ModelForm):
    machines = forms.ModelMultipleChoiceField(
        queryset=Machine.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label='Máquinas disponíveis',
    )

    class Meta:
        model = Production
        fields = ('description', 'quantity')

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

        if user is None:
            self.fields['machines'].queryset = Machine.objects.none()
            return

        active_machine_ids = ProductionMachine.objects.filter(
            production__status__in=[ProductionStatus.STANDBY, ProductionStatus.ONGOING]
        ).values_list('machine_id', flat=True)

        self.fields['machines'].queryset = (
            Machine.objects.filter(owner=user)
            .exclude(id__in=active_machine_ids)
            .order_by('model', 'serialnumber')
        )

        self.fields['machines'].label_from_instance = lambda m: f'{m.model} / {m.serialnumber}'

    def clean(self):
        cleaned = super().clean()
        machines = cleaned.get('machines')
        if not machines:
            raise forms.ValidationError('Não é permitido cadastrar uma produção sem máquinas associadas.')

        if self.user is None:
            raise forms.ValidationError('Usuário inválido')

        not_owned = machines.exclude(owner=self.user).exists()
        if not_owned:
            raise forms.ValidationError('Você só pode selecionar máquinas de sua propriedade.')

        active_machine_ids = set(
            ProductionMachine.objects.filter(
                machine__in=machines,
                production__status__in=[ProductionStatus.STANDBY, ProductionStatus.ONGOING],
            ).values_list('machine_id', flat=True)
        )
        if active_machine_ids:
            raise forms.ValidationError('Uma ou mais máquinas selecionadas já estão vinculadas a outra produção ativa.')

        return cleaned

    def save(self, commit=True):
        production: Production = super().save(commit=False)
        production.user = self.user
        production.status = ProductionStatus.STANDBY
        if commit:
            production.save()

            machines = self.cleaned_data['machines']
            ProductionMachine.objects.bulk_create(
                [
                    ProductionMachine(
                        production=production,
                        machine=machine,
                        status=ProductionMachineStatus.STANDBY,
                    )
                    for machine in machines
                ]
            )
        return production