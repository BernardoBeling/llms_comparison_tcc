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

class User(AbstractUser, BaseModel):
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    cnpj = models.CharField(max_length=18)
    is_premium = models.BooleanField(default=False) # Requisito 1.1

    def __str__(self):
        return self.username

class Machine(BaseModel):
    model = models.CharField(max_length=255)
    serialnumber = models.CharField(max_length=255)
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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='STANDBY')
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)
    machines = models.ManyToManyField(Machine, through='ProductionMachine')

class ProductionMachine(BaseModel):
    STATUS_CHOICES = [
        ('STANDBY', 'Standby'),
        ('ONGOING', 'Ongoing'),
        ('HALT', 'Halt'),
        ('FINISHED', 'Finished'),
        ('CANCELED', 'Canceled'),
    ]
    production = models.ForeignKey(Production, on_delete=models.CASCADE)
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='STANDBY')
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)
    working_time = models.IntegerField(default=0) # Requisito 2.1 (Minutos)

    def save(self, *args, **kwargs):
        # Requisito 2.2: Cálculo automático do working_time
        if self.started_at:
            end_time = None
            if self.status == 'FINISHED' and self.finished_at:
                end_time = self.finished_at
            elif self.status == 'CANCELED' and self.canceled_at:
                end_time = self.canceled_at
            
            if end_time:
                diff = end_time - self.started_at
                self.working_time = int(diff.total_seconds() // 60)
        
        super().save(*args, **kwargs)