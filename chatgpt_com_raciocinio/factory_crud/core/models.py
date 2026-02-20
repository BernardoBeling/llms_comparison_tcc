from django.conf import settings
from django.db import models
from django.utils import timezone


class SoftDeleteQuerySet(models.QuerySet):
    def delete(self):
        return super().update(deleted_at=timezone.now())

    def hard_delete(self):
        return super().delete()


class SoftDeleteManager(models.Manager):
    def get_queryset(self):
        return SoftDeleteQuerySet(self.model, using=self._db).filter(deleted_at__isnull=True)


class BaseModel(models.Model):
    """
    Base Model (conceitual):
      - id (autoincrement) -> fornecido pelo Django automaticamente (BigAutoField por default)
      - created_at (TIMESTAMP)
      - updated_at (TIMESTAMP)
      - deleted_at (TIMESTAMP, soft delete)
    """
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True, default=None)

    objects = SoftDeleteManager()
    all_objects = models.Manager()

    class Meta:
        abstract = True

    def delete(self, using=None, keep_parents=False):
        self.deleted_at = timezone.now()
        self.save(update_fields=["deleted_at"])


class ProductionStatus(models.TextChoices):
    STANDBY = "STANDBY", "STANDBY"
    ONGOING = "ONGOING", "ONGOING"
    FINISHED = "FINISHED", "FINISHED"
    CANCELED = "CANCELED", "CANCELED"


class ProductionMachineStatus(models.TextChoices):
    STANDBY = "STANDBY", "STANDBY"
    ONGOING = "ONGOING", "ONGOING"
    HALT = "HALT", "HALT"
    FINISHED = "FINISHED", "FINISHED"
    CANCELED = "CANCELED", "CANCELED"


class Machine(BaseModel):
    model = models.CharField(max_length=255)
    serialnumber = models.CharField(max_length=255, unique=True)
    owner_user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="machines",
    )

    def __str__(self):
        return f"{self.model} / {self.serialnumber}"


class Production(BaseModel):
    description = models.CharField(max_length=255)
    quantity = models.PositiveIntegerField()
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="productions",
    )
    status = models.CharField(max_length=32, choices=ProductionStatus.choices, default=ProductionStatus.STANDBY)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Production #{self.id} - {self.description}"

    def can_finish(self) -> bool:
        machines = self.production_machines.all()
        if not machines.exists():
            return False
        return all(pm.status not in [ProductionMachineStatus.STANDBY, ProductionMachineStatus.ONGOING] for pm in machines)

    def set_status(self, new_status: str):
        now = timezone.now()
        self.status = new_status
        if new_status == ProductionStatus.ONGOING and self.started_at is None:
            self.started_at = now
        if new_status == ProductionStatus.FINISHED and self.finished_at is None:
            self.finished_at = now
        if new_status == ProductionStatus.CANCELED and self.canceled_at is None:
            self.canceled_at = now
        self.save()


class ProductionMachine(BaseModel):
    production = models.ForeignKey(
        Production,
        on_delete=models.CASCADE,
        related_name="production_machines",
    )
    machine = models.ForeignKey(
        Machine,
        on_delete=models.PROTECT,
        related_name="machine_productions",
    )
    status = models.CharField(max_length=32, choices=ProductionMachineStatus.choices, default=ProductionMachineStatus.STANDBY)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    canceled_at = models.DateTimeField(null=True, blank=True)

    # ✅ Incremental: tempo total de operação (minutos)
    working_time = models.PositiveIntegerField(default=0)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["production", "machine"], name="uniq_production_machine_pair"),
        ]

    def __str__(self):
        return f"{self.production_id} - {self.machine}"

    def _recalculate_working_time_if_possible(self):
        """
        Regra incremental:
        - working_time é calculado quando:
          - FINISHED: started_at -> finished_at
          - CANCELED: started_at -> canceled_at
        - Se não houver started_at ou end_at válido, mantém 0.
        - Considera apenas ciclos válidos do lifecycle existente.
        """
        if not self.started_at:
            return

        end_at = None
        if self.status == ProductionMachineStatus.FINISHED:
            end_at = self.finished_at
        elif self.status == ProductionMachineStatus.CANCELED:
            end_at = self.canceled_at

        if not end_at:
            return

        delta_seconds = (end_at - self.started_at).total_seconds()
        if delta_seconds < 0:
            return

        minutes = int(delta_seconds // 60)  # floor
        self.working_time = minutes

    def set_status(self, new_status: str):
        now = timezone.now()
        self.status = new_status

        if new_status == ProductionMachineStatus.ONGOING and self.started_at is None:
            self.started_at = now

        if new_status == ProductionMachineStatus.FINISHED and self.finished_at is None:
            self.finished_at = now

        if new_status == ProductionMachineStatus.CANCELED and self.canceled_at is None:
            self.canceled_at = now

        # ✅ calcula working_time automaticamente quando encerrar
        self._recalculate_working_time_if_possible()

        self.save()
