from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils import timezone

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True

class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email: raise ValueError('Email obrigatório')
        email = self.normalize_email(email)
        user = self.model(email=email, username=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    cnpj = models.CharField(max_length=18)
    is_premium = models.BooleanField(default=False)
    theme_mode = models.CharField(max_length=10, default='light')
    
    first_name = None
    last_name = None
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name', 'cnpj']
    
    objects = UserManager()

class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

class Machine(BaseModel):
    model = models.CharField(max_length=100)
    serialnumber = models.CharField(max_length=100, unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='machines')
    
    objects = SoftDeleteManager()
    all_objects = models.Manager()

class Production(BaseModel):
    STATUS_CHOICES = [('STANDBY', 'Standby'), ('ONGOING', 'Ongoing'), ('FINISHED', 'Finished'), ('CANCELED', 'Canceled')]
    description = models.CharField(max_length=255)
    quantity = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='STANDBY')
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)
    
    objects = SoftDeleteManager()

class ProductionMachine(BaseModel):
    STATUS_CHOICES = [('STANDBY', 'Standby'), ('ONGOING', 'Ongoing'), ('HALT', 'Halt'), ('FINISHED', 'Finished'), ('CANCELED', 'Canceled')]
    production = models.ForeignKey(Production, on_delete=models.CASCADE)
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='STANDBY')
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)
    working_time = models.IntegerField(default=0)
    
    objects = SoftDeleteManager()

    def save(self, *args, **kwargs):
        # Cálculo robusto de tempo
        if self.started_at:
            end_ref = None
            if self.status == 'FINISHED' and self.finished_at:
                end_ref = self.finished_at
            elif self.status == 'CANCELED' and self.canceled_at:
                end_ref = self.canceled_at
            
            if end_ref:
                diff = end_ref - self.started_at
                self.working_time = max(0, int(diff.total_seconds() // 60))
        else:
            self.working_time = 0
            
        super().save(*args, **kwargs)