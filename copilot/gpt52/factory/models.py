from __future__ import annotations

from django.conf import settings
from django.db import models, transaction
from django.utils import timezone

from core.common.models import BaseModel


class Machine(BaseModel):
	model = models.CharField(max_length=255)
	serialnumber = models.CharField(max_length=255, unique=True)
	owner = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.PROTECT,
		related_name='machines',
		db_column='owner_user_id',
	)

	class Meta:
		ordering = ('-id',)

	def __str__(self):
		return f'{self.model} / {self.serialnumber}'


class ProductionStatus(models.TextChoices):
	STANDBY = 'STANDBY', 'STANDBY'
	ONGOING = 'ONGOING', 'ONGOING'
	FINISHED = 'FINISHED', 'FINISHED'
	CANCELED = 'CANCELED', 'CANCELED'


class Production(BaseModel):
	description = models.CharField(max_length=255)
	quantity = models.PositiveIntegerField()
	user = models.ForeignKey(
		settings.AUTH_USER_MODEL,
		on_delete=models.PROTECT,
		related_name='productions',
		db_column='user_id',
	)
	status = models.CharField(max_length=16, choices=ProductionStatus.choices, default=ProductionStatus.STANDBY)
	machines = models.ManyToManyField(Machine, through='ProductionMachine', related_name='productions')
	started_at = models.DateTimeField(null=True, blank=True)
	finished_at = models.DateTimeField(null=True, blank=True)
	canceled_at = models.DateTimeField(null=True, blank=True)

	class Meta:
		ordering = ('-id',)

	def __str__(self):
		return f'#{self.id} - {self.description}'

	def can_finish(self) -> bool:
		forbidden = {ProductionMachineStatus.STANDBY, ProductionMachineStatus.ONGOING}
		return not self.machines.through.objects.filter(
			production=self,
			status__in=forbidden,
		).exists()

	@transaction.atomic
	def cancel(self):
		now = timezone.now()
		self.status = ProductionStatus.CANCELED
		self.canceled_at = now
		self.save(update_fields=['status', 'canceled_at', 'updated_at'])

		for pm in ProductionMachine.objects.filter(production=self):
			pm.cancel(cancel_time=now)

	@transaction.atomic
	def finish(self):
		if not self.can_finish():
			raise ValueError('Não é permitido finalizar enquanto houver máquinas em STANDBY ou ONGOING')

		now = timezone.now()
		self.status = ProductionStatus.FINISHED
		self.finished_at = now
		self.save(update_fields=['status', 'finished_at', 'updated_at'])

		# Ao finalizar a produção, garante timestamps e working_time para associações ainda abertas.
		for pm in ProductionMachine.objects.filter(production=self, finished_at__isnull=True, canceled_at__isnull=True):
			pm.finish(finish_time=now)

	@transaction.atomic
	def start(self):
		if self.status in {ProductionStatus.FINISHED, ProductionStatus.CANCELED}:
			raise ValueError('Produção já encerrada')

		if self.status == ProductionStatus.ONGOING:
			return

		now = timezone.now()
		self.status = ProductionStatus.ONGOING
		self.started_at = self.started_at or now
		self.save(update_fields=['status', 'started_at', 'updated_at'])

		# Inicia todas as máquinas associadas que ainda estão em STANDBY
		ProductionMachine.objects.filter(
			production=self,
			status=ProductionMachineStatus.STANDBY,
			started_at__isnull=True,
		).update(status=ProductionMachineStatus.ONGOING, started_at=now)


class ProductionMachineStatus(models.TextChoices):
	STANDBY = 'STANDBY', 'STANDBY'
	ONGOING = 'ONGOING', 'ONGOING'
	HALT = 'HALT', 'HALT'
	FINISHED = 'FINISHED', 'FINISHED'
	CANCELED = 'CANCELED', 'CANCELED'


class ProductionMachine(BaseModel):
	production = models.ForeignKey(
		Production,
		on_delete=models.CASCADE,
		related_name='production_machines',
		db_column='production_id',
	)
	machine = models.ForeignKey(
		Machine,
		on_delete=models.PROTECT,
		related_name='production_machines',
		db_column='machine_id',
	)
	status = models.CharField(max_length=16, choices=ProductionMachineStatus.choices, default=ProductionMachineStatus.STANDBY)
	started_at = models.DateTimeField(null=True, blank=True)
	finished_at = models.DateTimeField(null=True, blank=True)
	canceled_at = models.DateTimeField(null=True, blank=True)
	working_time = models.PositiveIntegerField(default=0)

	class Meta:
		ordering = ('id',)
		constraints = [
			models.UniqueConstraint(fields=['production', 'machine'], name='uniq_production_machine'),
		]

	def __str__(self):
		return f'{self.machine} ({self.status})'

	def _compute_working_time_minutes(self, end_time):
		if not self.started_at or not end_time:
			return 0
		delta_seconds = (end_time - self.started_at).total_seconds()
		if delta_seconds <= 0:
			return 0
		return int(delta_seconds // 60)

	def cancel(self, cancel_time=None):
		if self.status in {ProductionMachineStatus.FINISHED, ProductionMachineStatus.CANCELED}:
			return
		now = cancel_time or timezone.now()
		# Se nunca foi iniciada, considera tempo 0
		self.status = ProductionMachineStatus.CANCELED
		self.canceled_at = now
		self.working_time = self._compute_working_time_minutes(now)
		self.save(update_fields=['status', 'canceled_at', 'working_time', 'updated_at'])

	def finish(self, finish_time=None):
		if self.status in {ProductionMachineStatus.FINISHED, ProductionMachineStatus.CANCELED}:
			return
		now = finish_time or timezone.now()
		self.status = ProductionMachineStatus.FINISHED
		self.finished_at = now
		self.working_time = self._compute_working_time_minutes(now)
		self.save(update_fields=['status', 'finished_at', 'working_time', 'updated_at'])

# Create your models here.
