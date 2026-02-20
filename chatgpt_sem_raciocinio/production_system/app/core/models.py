from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class BaseModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class User(AbstractUser, BaseModel):
    name = models.CharField(max_length=255)
    cnpj = models.CharField(max_length=20)
    is_premium = models.BooleanField(default=False)

    def max_machines_allowed(self):
        return 10 if self.is_premium else 5


class Machine(BaseModel):
    model = models.CharField(max_length=255)
    serialnumber = models.CharField(max_length=255, unique=True)
    owner_user = models.ForeignKey(User, on_delete=models.CASCADE)

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
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)

    def cancel(self):
        if self.status in ['FINISHED', 'CANCELED']:
            return

        now = timezone.now()
        self.status = 'CANCELED'
        self.canceled_at = now
        self.save()

        for pm in self.productionmachine_set.all():
            pm.cancel()

    def try_finish(self):
        pending = self.productionmachine_set.filter(
            status__in=['STANDBY', 'ONGOING']
        ).exists()

        if not pending:
            now = timezone.now()
            self.status = 'FINISHED'
            self.finished_at = now
            self.save()


# class ProductionMachine(BaseModel):
#     STATUS_CHOICES = [
#         ('STANDBY', 'Standby'),
#         ('ONGOING', 'Ongoing'),
#         ('HALT', 'Halt'),
#         ('FINISHED', 'Finished'),
#         ('CANCELED', 'Canceled'),
#     ]

#     production = models.ForeignKey(Production, on_delete=models.CASCADE)
#     machine = models.ForeignKey(Machine, on_delete=models.CASCADE)
#     status = models.CharField(max_length=20, choices=STATUS_CHOICES)
#     started_at = models.DateTimeField(null=True, blank=True)
#     finished_at = models.DateTimeField(null=True, blank=True)
#     canceled_at = models.DateTimeField(null=True, blank=True)
#     working_time = models.IntegerField(default=0)  # minutos

#     def calculate_working_time(self):
#         end_time = self.finished_at or self.canceled_at
#         if self.started_at and end_time:
#             delta = end_time - self.started_at
#             self.working_time = int(delta.total_seconds() / 60)
#             self.save()

#     def cancel(self):
#         if self.status in ['FINISHED', 'CANCELED']:
#             return

#         now = timezone.now()
#         self.status = 'CANCELED'
#         self.canceled_at = now
#         self._calculate_working_time(now)
#         self.save()

#     def finish(self):
#         if self.status in ['FINISHED', 'CANCELED']:
#             return

#         now = timezone.now()
#         self.status = 'FINISHED'
#         self.finished_at = now
#         self._calculate_working_time(now)
#         self.save()

class ProductionMachine(BaseModel):
    production = models.ForeignKey(
        'Production',
        on_delete=models.CASCADE
    )
    machine = models.ForeignKey(
        'Machine',
        on_delete=models.CASCADE
    )

    status = models.CharField(max_length=20)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)
    working_time = models.PositiveIntegerField(default=0)  # minutos

    def _calculate_working_time(self, end_time):
        if self.started_at:
            delta = end_time - self.started_at
            self.working_time = int(delta.total_seconds() / 60)

    def cancel(self):
        if self.status in ['FINISHED', 'CANCELED']:
            return

        now = timezone.now()
        self.status = 'CANCELED'
        self.canceled_at = now
        self._calculate_working_time(now)
        self.save()

    def finish(self):
        if self.status in ['FINISHED', 'CANCELED']:
            return

        now = timezone.now()
        self.status = 'FINISHED'
        self.finished_at = now
        self._calculate_working_time(now)
        self.save()