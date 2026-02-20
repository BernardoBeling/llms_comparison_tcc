from __future__ import annotations

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.views import View

from .forms import LoginForm, SignupForm


class SignupView(View):
	template_name = 'accounts/signup.html'

	def get(self, request):
		if request.user.is_authenticated:
			return redirect('dashboard')
		form = SignupForm()
		return render(request, self.template_name, {'form': form})

	def post(self, request):
		if request.user.is_authenticated:
			return redirect('dashboard')

		form = SignupForm(request.POST)
		if form.is_valid():
			user = form.save()
			login(request, user)
			messages.success(request, 'Conta criada com sucesso!')
			return redirect('dashboard')

		return render(request, self.template_name, {'form': form})


class AppLoginView(LoginView):
	authentication_form = LoginForm
	template_name = 'accounts/login.html'
	redirect_authenticated_user = True


class AppLogoutView(LogoutView):
	next_page = reverse_lazy('login')
