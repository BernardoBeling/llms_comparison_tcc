from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView

from .forms import SignUpForm
from .models import User


class SignUpView(CreateView):
    model = User
    form_class = SignUpForm
    template_name = "registration/signup.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        form.save()
        messages.success(self.request, "Usuário criado com sucesso. Agora faça login.")
        return redirect(self.success_url)
