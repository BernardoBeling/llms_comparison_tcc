from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError

from .models import User


class SignUpForm(UserCreationForm):
    name = forms.CharField(max_length=255, required=True, label="Nome")
    email = forms.EmailField(required=True, label="E-mail")
    cnpj = forms.CharField(max_length=32, required=False, label="CNPJ")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "name", "email", "cnpj", "password1", "password2")

    def clean_email(self):
        email = (self.cleaned_data.get("email") or "").strip().lower()
        if not email:
            raise ValidationError("E-mail é obrigatório.")
        if User.all_objects.filter(email=email).exists():
            raise ValidationError("Já existe um usuário com este e-mail.")
        return email

    def clean_username(self):
        username = (self.cleaned_data.get("username") or "").strip()
        if not username:
            raise ValidationError("Username é obrigatório.")
        if User.all_objects.filter(username=username).exists():
            raise ValidationError("Já existe um usuário com este username.")
        return username

    def save(self, commit=True):
        user = super().save(commit=False)
        user.name = self.cleaned_data["name"].strip()
        user.email = self.cleaned_data["email"].strip().lower()
        user.cnpj = (self.cleaned_data.get("cnpj") or "").strip()
        if commit:
            user.save()
        return user
