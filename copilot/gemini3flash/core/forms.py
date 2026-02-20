from django import forms
from .models import Machine, Production, User

class MachineForm(forms.ModelForm):
    class Meta:
        model = Machine
        fields = ['model', 'serialnumber']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        if self.user and not self.instance.pk:
            limit = 10 if self.user.is_premium else 5
            if Machine.objects.filter(owner=self.user).count() >= limit:
                raise forms.ValidationError(f"Você já atingiu o limite de {limit} máquinas para sua conta.")
        return cleaned_data

class ProductionForm(forms.ModelForm):
    machines = forms.ModelMultipleChoiceField(
        queryset=Machine.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        label="Máquinas (MODEL / SERIALNUMBER)"
    )

    class Meta:
        model = Production
        fields = ['description', 'quantity']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user:
            # Requisito: Máquinas do proprietário e disponíveis
            # Disponível: não vinculada a produção não finalizada/cancelada
            busy_machines = Machine.objects.filter(
                machine_productions__production__status__in=['STANDBY', 'ONGOING']
            ).distinct()
            
            self.fields['machines'].queryset = Machine.objects.filter(
                owner=self.user
            ).exclude(id__in=busy_machines)

    def clean_machines(self):
        machines = self.cleaned_data.get('machines')
        if not machines:
            raise forms.ValidationError("Uma produção deve ter pelo menos uma máquina associada.")
        return machines

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)
    confirm_password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'name', 'email', 'cnpj', 'password']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("As senhas não conferem.")
        return cleaned_data
