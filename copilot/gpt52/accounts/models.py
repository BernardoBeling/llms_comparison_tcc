from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.models import PermissionsMixin
from django.db import models
from django.utils import timezone

from core.common.models import BaseModel


class UserManager(BaseUserManager):
	use_in_migrations = True

	def create_user(self, name: str, email: str, cnpj: str, password: str | None = None, **extra_fields):
		if not name:
			raise ValueError('O campo name é obrigatório')
		if not email:
			raise ValueError('O campo email é obrigatório')
		if not cnpj:
			raise ValueError('O campo cnpj é obrigatório')

		email = self.normalize_email(email)

		user = self.model(
			name=name,
			email=email,
			cnpj=cnpj,
			**extra_fields,
		)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_superuser(self, name: str, email: str, cnpj: str, password: str | None = None, **extra_fields):
		extra_fields.setdefault('is_staff', True)
		extra_fields.setdefault('is_superuser', True)
		extra_fields.setdefault('is_active', True)

		if extra_fields.get('is_staff') is not True:
			raise ValueError('Superuser precisa ter is_staff=True')
		if extra_fields.get('is_superuser') is not True:
			raise ValueError('Superuser precisa ter is_superuser=True')

		return self.create_user(name=name, email=email, cnpj=cnpj, password=password, **extra_fields)


class User(BaseModel, AbstractBaseUser, PermissionsMixin):
	name = models.CharField(max_length=255, unique=True)
	email = models.EmailField(max_length=255)
	cnpj = models.CharField(max_length=32)
	is_premium = models.BooleanField(default=False)

	is_staff = models.BooleanField(default=False)
	is_active = models.BooleanField(default=True)
	date_joined = models.DateTimeField(default=timezone.now)

	objects = UserManager()

	USERNAME_FIELD = 'name'
	REQUIRED_FIELDS = ['email', 'cnpj']

	def __str__(self):
		return self.name

# Create your models here.
