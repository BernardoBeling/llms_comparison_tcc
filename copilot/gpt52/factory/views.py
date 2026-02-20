from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views.decorators.http import require_POST

from .forms import MachineForm, ProductionForm
from .models import (
	Machine,
	Production,
	ProductionMachine,
	ProductionMachineStatus,
	ProductionStatus,
)


@login_required
def dashboard(request):
	productions = Production.objects.filter(user=request.user).order_by('-id')

	ongoing_count = productions.filter(status=ProductionStatus.ONGOING).count()

	used_machine_ids = ProductionMachine.objects.filter(
		production__status__in=[ProductionStatus.STANDBY, ProductionStatus.ONGOING],
		machine__owner=request.user,
	).values_list('machine_id', flat=True)

	total_machines = Machine.objects.filter(owner=request.user).count()
	used_machines = Machine.objects.filter(owner=request.user, id__in=used_machine_ids).distinct().count()
	available_machines = total_machines - used_machines

	return render(
		request,
		'factory/dashboard.html',
		{
			'productions': productions,
			'ongoing_count': ongoing_count,
			'used_machines': used_machines,
			'available_machines': available_machines,
		},
	)


@login_required
def machine_list(request):
	machines = Machine.objects.filter(owner=request.user).order_by('-id')
	if request.method == 'POST':
		form = MachineForm(request.POST, user=request.user)
		if form.is_valid():
			try:
				form.save()
				messages.success(request, 'Máquina cadastrada com sucesso!')
				return redirect('machine_list')
			except Exception as exc:
				messages.error(request, str(exc))
	else:
		form = MachineForm(user=request.user)

	return render(request, 'factory/machines.html', {'machines': machines, 'form': form})


@login_required
def production_list(request):
	productions = (
		Production.objects.filter(user=request.user)
		.prefetch_related('production_machines__machine')
		.order_by('-id')
	)

	if request.method == 'POST':
		form = ProductionForm(request.POST, user=request.user)
		if form.is_valid():
			production = form.save()
			messages.success(request, 'Produção cadastrada com sucesso!')
			return redirect('production_detail', production_id=production.id)
	else:
		form = ProductionForm(user=request.user)

	return render(request, 'factory/productions.html', {'productions': productions, 'form': form})


@login_required
def production_detail(request, production_id: int):
	production = get_object_or_404(Production, id=production_id, user=request.user)
	pms = ProductionMachine.objects.filter(production=production).select_related('machine').order_by('id')
	return render(
		request,
		'factory/production_detail.html',
		{
			'production': production,
			'pms': pms,
			'can_finish': production.can_finish(),
		},
	)


@require_POST
@login_required
def production_start(request, production_id: int):
	production = get_object_or_404(Production, id=production_id, user=request.user)
	try:
		production.start()
		messages.success(request, 'Produção iniciada (ONGOING).')
	except Exception as exc:
		messages.error(request, str(exc))
	return redirect('production_detail', production_id=production.id)


@require_POST
@login_required
def production_cancel(request, production_id: int):
	production = get_object_or_404(Production, id=production_id, user=request.user)
	try:
		production.cancel()
		messages.success(request, 'Produção cancelada. Todas as máquinas associadas foram canceladas.')
	except Exception as exc:
		messages.error(request, str(exc))
	return redirect('production_detail', production_id=production.id)


@require_POST
@login_required
def production_finish(request, production_id: int):
	production = get_object_or_404(Production, id=production_id, user=request.user)
	try:
		production.finish()
		messages.success(request, 'Produção finalizada.')
	except Exception as exc:
		messages.error(request, str(exc))
	return redirect('production_detail', production_id=production.id)


def _get_pm_for_user(user, production_id: int, pm_id: int) -> ProductionMachine:
	pm = get_object_or_404(ProductionMachine, id=pm_id, production_id=production_id)
	if pm.production.user_id != user.id:
		raise Http404()
	return pm


@require_POST
@login_required
def production_machine_cancel(request, production_id: int, pm_id: int):
	pm = _get_pm_for_user(request.user, production_id, pm_id)
	if pm.started_at is None and pm.production.started_at is not None:
		pm.started_at = pm.production.started_at
		pm.save(update_fields=['started_at', 'updated_at'])
	pm.cancel()
	messages.success(request, 'Execução cancelada para esta máquina (sem alterar a produção).')
	return redirect('production_detail', production_id=production_id)


@require_POST
@login_required
def production_machine_finish(request, production_id: int, pm_id: int):
	pm = _get_pm_for_user(request.user, production_id, pm_id)
	if pm.started_at is None and pm.production.started_at is not None:
		pm.started_at = pm.production.started_at
		pm.save(update_fields=['started_at', 'updated_at'])
	pm.finish()
	messages.success(request, 'Máquina marcada como FINISHED (sem alterar a produção).')
	return redirect('production_detail', production_id=production_id)


@require_POST
@login_required
def machine_delete(request, machine_id: int):
	machine = get_object_or_404(Machine, id=machine_id, owner=request.user)
	is_in_active_production = ProductionMachine.objects.filter(
		machine=machine,
		production__status__in=[ProductionStatus.STANDBY, ProductionStatus.ONGOING],
	).exists()
	if is_in_active_production:
		messages.error(request, 'Não é possível excluir uma máquina vinculada a uma produção ativa.')
		return redirect('machine_list')

	machine.delete()
	messages.success(request, 'Máquina excluída (soft delete).')
	return redirect('machine_list')


@require_POST
@login_required
def production_delete(request, production_id: int):
	production = get_object_or_404(Production, id=production_id, user=request.user)
	if production.status not in {ProductionStatus.FINISHED, ProductionStatus.CANCELED}:
		messages.error(request, 'Para excluir, primeiro cancele ou finalize a produção.')
		return redirect('production_detail', production_id=production.id)

	# Soft delete produção e vínculos
	for pm in ProductionMachine.objects.filter(production=production):
		pm.delete()
	production.delete()

	messages.success(request, 'Produção excluída (soft delete).')
	return redirect('production_list')
