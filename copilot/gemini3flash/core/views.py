from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.utils import timezone
from .models import Machine, Production, ProductionMachine
from .forms import MachineForm, ProductionForm, UserRegistrationForm
from django.db.models import Count, Q

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            login(request, user)
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def home(request):
    user = request.user
    productions = Production.objects.filter(user=user)
    
    ongoing_count = productions.filter(status='ONGOING').count()
    
    # Máquinas utilizadas (em produções não finalizadas/canceladas)
    used_machines = Machine.objects.filter(
        owner=user,
        machine_productions__production__status__in=['STANDBY', 'ONGOING']
    ).distinct().count()
    
    total_machines = Machine.objects.filter(owner=user).count()
    available_machines = total_machines - used_machines
    
    return render(request, 'core/home.html', {
        'productions': productions,
        'ongoing_count': ongoing_count,
        'used_machines': used_machines,
        'available_machines': available_machines
    })

@login_required
def machine_list(request):
    machines = Machine.objects.filter(owner=request.user)
    limit = 10 if request.user.is_premium else 5
    if request.method == 'POST':
        form = MachineForm(request.POST, user=request.user)
        if form.is_valid():
            machine = form.save(commit=False)
            machine.owner = request.user
            machine.save()
            return redirect('machine_list')
    else:
        form = MachineForm(user=request.user)
    return render(request, 'core/machine_list.html', {
        'machines': machines, 
        'form': form,
        'limit': limit
    })

@login_required
def production_create(request):
    if request.method == 'POST':
        form = ProductionForm(request.POST, user=request.user)
        if form.is_valid():
            production = form.save(commit=False)
            production.user = request.user
            production.save()
            
            machines = form.cleaned_data['machines']
            for machine in machines:
                ProductionMachine.objects.create(
                    production=production,
                    machine=machine,
                    status='STANDBY'
                )
            return redirect('home')
    else:
        form = ProductionForm(user=request.user)
    return render(request, 'core/production_form.html', {'form': form})

@login_required
def production_start(request, pk):
    production = get_object_or_404(Production, pk=pk, user=request.user)
    if production.status == 'STANDBY':
        production.status = 'ONGOING'
        production.started_at = timezone.now()
        production.save()
        
        # Atualiza todas as máquinas da produção
        production.production_machines.update(status='ONGOING', started_at=timezone.now())
        
    return redirect('home')

@login_required
def production_cancel(request, pk):
    production = get_object_or_404(Production, pk=pk, user=request.user)
    if production.status in ['STANDBY', 'ONGOING']:
        now = timezone.now()
        production.status = 'CANCELED'
        production.canceled_at = now
        production.save()
        
        # Cancela todas as máquinas e calcula o tempo
        pms = production.production_machines.filter(
            status__in=['STANDBY', 'ONGOING']
        )
        for pm in pms:
            pm.status = 'CANCELED'
            pm.canceled_at = now
            pm.calculate_working_time()
            pm.save()
        
    return redirect('home')

@login_required
def production_finish(request, pk):
    production = get_object_or_404(Production, pk=pk, user=request.user)
    
    # Requisito 6: Finalizada quando todas as máquinas têm status diferente de STANDBY e ONGOING
    active_machines = production.production_machines.filter(status__in=['STANDBY', 'ONGOING']).exists()
    
    if not active_machines and production.status == 'ONGOING':
        production.status = 'FINISHED'
        production.finished_at = timezone.now()
        production.save()
        
    return redirect('home')

@login_required
def machine_cancel(request, pm_pk):
    pm = get_object_or_404(ProductionMachine, pk=pm_pk, production__user=request.user)
    if pm.status in ['STANDBY', 'ONGOING']:
        pm.status = 'CANCELED'
        pm.canceled_at = timezone.now()
        pm.calculate_working_time()
        pm.save()
    return redirect('home')

@login_required
def machine_finish(request, pm_pk):
    pm = get_object_or_404(ProductionMachine, pk=pm_pk, production__user=request.user)
    if pm.status == 'ONGOING':
        pm.status = 'FINISHED'
        pm.finished_at = timezone.now()
        pm.calculate_working_time()
        pm.save()
    return redirect('home')
