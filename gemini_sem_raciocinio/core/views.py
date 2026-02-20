from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .models import Machine, Production, ProductionMachine
from .forms import MachineForm, ProductionForm
from .forms import UserRegistrationForm

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Conta criada com sucesso! Faça login.")
            return redirect('login')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@login_required
def dashboard(request):
    productions = Production.objects.filter(user=request.user).order_by('-created_at')
    
    # Máquinas do usuário que estão em produções ativas
    busy_machine_ids = ProductionMachine.objects.filter(
        production__status__in=['STANDBY', 'ONGOING'],
        machine__owner=request.user
    ).values_list('machine_id', flat=True)
    
    total_machines = Machine.objects.filter(owner=request.user)
    
    context = {
        'ongoing_count': productions.filter(status='ONGOING').count(),
        'machines_used': total_machines.filter(id__in=busy_machine_ids).count(),
        'machines_available': total_machines.exclude(id__in=busy_machine_ids).count(),
        'productions': productions
    }
    return render(request, 'dashboard.html', context)

@login_required
def machine_create(request):
    # Requisito 1.2: Lógica de limite dinâmico
    limit = 10 if request.user.is_premium else 5
    if Machine.objects.filter(owner=request.user).count() >= limit:
        messages.error(request, f"Limite de {limit} máquinas atingido para seu plano.")
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = MachineForm(request.POST)
        if form.is_valid():
            machine = form.save(commit=False)
            machine.owner = request.user
            machine.save()
            return redirect('dashboard')
    else:
        form = MachineForm()
    return render(request, 'machine_form.html', {'form': form})

@login_required
def production_create(request):
    if request.method == 'POST':
        form = ProductionForm(request.POST, user=request.user)
        if form.is_valid():
            prod = form.save(commit=False)
            prod.user = request.user
            prod.status = 'ONGOING' # Inicia como Ongoing ao criar
            prod.started_at = timezone.now()
            prod.save()
            
            # Associa as máquinas selecionadas
            machines = form.cleaned_data['selected_machines']
            for m in machines:
                ProductionMachine.objects.create(
                    production=prod, 
                    machine=m, 
                    status='ONGOING', 
                    started_at=timezone.now()
                )
            
            messages.success(request, "Produção iniciada com sucesso.")
            return redirect('dashboard')
    else:
        form = ProductionForm(user=request.user)
    return render(request, 'production_form.html', {'form': form})

@login_required
def production_detail(request, pk):
    production = get_object_or_404(Production, pk=pk, user=request.user)
    items = ProductionMachine.objects.filter(production=production)
    
    # Requisito 6: Só pode finalizar produção se todas as máquinas forem FINISHED ou CANCELED
    # Ou seja, não pode haver nenhuma em STANDBY ou ONGOING
    active_machines = items.filter(status__in=['STANDBY', 'ONGOING', 'HALT']).exists()
    can_finish_production = not active_machines and production.status == 'ONGOING'
    
    return render(request, 'production_detail.html', {
        'production': production,
        'items': items,
        'can_finish': can_finish_production
    })

@login_required
def production_cancel(request, pk):
    production = get_object_or_404(Production, pk=pk, user=request.user)
    production.status = 'CANCELED'
    production.canceled_at = timezone.now()
    production.save()
    
    # Requisito 5: Cancelar simultaneamente todas as máquinas associadas
    ProductionMachine.objects.filter(production=production).update(
        status='CANCELED', 
        canceled_at=timezone.now()
    )
    
    messages.warning(request, "Produção e todas as suas máquinas foram canceladas.")
    return redirect('dashboard')

@login_required
def production_finish(request, pk):
    production = get_object_or_404(Production, pk=pk, user=request.user)
    
    # Verificação extra de segurança
    if not ProductionMachine.objects.filter(production=production, status__in=['STANDBY', 'ONGOING']).exists():
        production.status = 'FINISHED'
        production.finished_at = timezone.now()
        production.save()
        messages.success(request, "Produção finalizada com sucesso.")
    else:
        messages.error(request, "Ação negada: Existem máquinas em execução.")
        
    return redirect('production_detail', pk=pk)

@login_required
def machine_cancel(request, pk):
    pm = get_object_or_404(ProductionMachine, pk=pk, production__user=request.user)
    pm.status = 'CANCELED'
    pm.canceled_at = timezone.now()
    pm.save()
    messages.warning(request, f"Execução da máquina {pm.machine.serialnumber} cancelada.")
    return redirect('production_detail', pk=pm.production.pk)

@login_required
def machine_finish(request, pk):
    """Finaliza a execução de uma máquina específica na produção"""
    pm = get_object_or_404(ProductionMachine, pk=pk, production__user=request.user)
    
    if pm.status in ['FINISHED', 'CANCELED']:
        messages.error(request, "Esta máquina já está em um estado final.")
    else:
        pm.status = 'FINISHED'
        pm.finished_at = timezone.now()
        pm.save()
        messages.success(request, f"Máquina {pm.machine.serialnumber} finalizada com sucesso.")
        
    return redirect('production_detail', pk=pm.production.pk)