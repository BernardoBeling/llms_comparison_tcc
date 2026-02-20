from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Machine, Production, ProductionMachine

class UserRegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "name", "email", "cnpj")

    def clean_cnpj(self):
        cnpj = self.cleaned_data.get('cnpj')
        # Aqui poderiam ser adicionadas validações matemáticas de CNPJ
        return cnpj

class MachineForm(forms.ModelForm):
    class Meta:
        model = Machine
        fields = ['model', 'serialnumber']

    def clean_serialnumber(self):
        sn = self.cleaned_data['serialnumber']
        if Machine.objects.filter(serialnumber=sn).exists():
            raise forms.ValidationError("Este número de série já está em uso.")
        return sn

class ProductionForm(forms.ModelForm):
    selected_machines = forms.ModelMultipleChoiceField(
        queryset=Machine.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        label="Máquinas Disponíveis"
    )

    class Meta:
        model = Production
        fields = ['description', 'quantity']

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
        
        # Filtra máquinas do usuário que não estão em produções ativas
        busy_machines = ProductionMachine.objects.filter(
            production__status__in=['STANDBY', 'ONGOING']
        ).values_list('machine_id', flat=True)
        
        # O label será formatado conforme o requisito: "MODEL / SERIALNUMBER"
        self.fields['selected_machines'].queryset = Machine.objects.filter(
            owner=user
        ).exclude(id__in=busy_machines)
        self.fields['selected_machines'].label_from_instance = lambda obj: f"{obj.model} / {obj.serialnumber}"