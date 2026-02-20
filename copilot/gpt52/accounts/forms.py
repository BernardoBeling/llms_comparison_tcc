from __future__ import annotations

from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

User = get_user_model()


class SignupForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('name', 'email', 'cnpj')


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label='Nome',
        widget=forms.TextInput(attrs={'autofocus': True}),
    )
