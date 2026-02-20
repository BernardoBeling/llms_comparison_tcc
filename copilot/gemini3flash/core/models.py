from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted_at__isnull=True)

class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self, **kwargs):
        self.deleted_at = timezone.now()
        self.save()

    def hard_delete(self, **kwargs):
        super().delete(**kwargs)

class User(AbstractUser, BaseModel):
    name = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=18)
    is_premium = models.BooleanField(default=False)

    def __str__(self):
        return self.username

class Machine(BaseModel):
    model = models.CharField(max_length=255)
    serialnumber = models.CharField(max_length=255, unique=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='machines')

    def __str__(self):
        return f"{self.model} / {self.serialnumber}"

class Production(BaseModel):
    STATUS_CHOICES = [
        ('STANDBY', 'Standby'),
        ('ONGOING', 'Ongoing'),
        ('FINISHED', 'Finished'),
        ('CANCELED', 'Canceled'),
    ]

    description = models.CharField(max_length=255)
    quantity = models.IntegerField()
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='productions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='STANDBY')
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.description

class ProductionMachine(BaseModel):
    STATUS_CHOICES = [
        ('STANDBY', 'Standby'),
        ('ONGOING', 'Ongoing'),
        ('HALT', 'Halt'),
        ('FINISHED', 'Finished'),
        ('CANCELED', 'Canceled'),
    ]

    production = models.ForeignKey(Production, on_delete=models.CASCADE, related_name='production_machines')
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='machine_productions')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='STANDBY')
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)
    working_time = models.IntegerField(default=0)

    def calculate_working_time(self):
        """Calcula o tempo de operação em minutos"""
        end_time = self.finished_at or self.canceled_at
        if self.started_at and end_time:
            diff = end_time - self.started_at
            self.working_time = int(diff.total_seconds() / 60)
        else:
            self.working_time = 0

    def __str__(self):
        return f"{self.production.description} - {self.machine.serialnumber}"
