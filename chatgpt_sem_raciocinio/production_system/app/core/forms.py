from django import forms
from .models import Machine, Production, User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError


# class MachineForm(forms.ModelForm):
#     class Meta:
#         model = Machine
#         fields = ['model', 'serialnumber']

#     def __init__(self, *args, **kwargs):
#         self.user = kwargs.pop('user')
#         super().__init__(*args, **kwargs)

#     def clean(self):
#         if Machine.objects.filter(owner_user=self.user).count() >= self.user.max_machines_allowed():
#             raise forms.ValidationError(
#                 f"Limite de máquinas atingido ({self.user.max_machines_allowed()})."
#             )
#         return self.cleaned_data

class MachineForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    class Meta:
        model = Machine
        fields = ['model', 'serialnumber']

    def clean(self):
        cleaned_data = super().clean()

        if not self.user:
            raise ValidationError('Usuário não identificado.')

        machine_count = Machine.objects.filter(owner_user=self.user).count()

        limit = 10 if self.user.is_premium else 5

        if machine_count >= limit:
            raise ValidationError(
                f'Limite de {limit} máquinas atingido para o seu plano.'
            )

        return cleaned_data
    
class ProductionForm(forms.ModelForm):
    machines = forms.ModelMultipleChoiceField(
        queryset=Machine.objects.none(),
        widget=forms.CheckboxSelectMultiple
    )

    class Meta:
        model = Production
        fields = ['description', 'quantity']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)

        busy_machines = Production.objects.filter(
            status__in=['STANDBY', 'ONGOING']
        ).values_list('productionmachine__machine_id', flat=True)

        self.fields['machines'].queryset = Machine.objects.filter(
            owner_user=user
        ).exclude(id__in=busy_machines)

class UserRegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['name', 'email', 'cnpj', 'password1', 'password2']