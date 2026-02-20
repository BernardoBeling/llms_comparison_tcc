from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.contrib import messages
from .models import Machine, Production, ProductionMachine, User

def register(request):
    if request.method == 'POST':
        user = User.objects.create_user(
            email=request.POST['email'],
            password=request.POST['password'],
            name=request.POST['name'],
            cnpj=request.POST['cnpj']
        )
        login(request, user)
        return redirect('dashboard')
    return render(request, 'register.html')

@login_required
def dashboard(request):
    # Listagem de todas as produções do usuário
    productions = Production.objects.filter(user=request.user).order_by('-created_at')
    
    # Queryset base das máquinas do usuário
    user_machines = Machine.objects.filter(owner=request.user)
    
    # Identificação de máquinas que estão atualmente vinculadas a produções ativas ou em espera
    # Consideramos "Em Uso" máquinas em produções STANDBY ou ONGOING, 
    # cujo status individual não seja FINISHED ou CANCELED.
    busy_ids = ProductionMachine.objects.filter(
        production__status__in=['STANDBY', 'ONGOING'],
        status__in=['STANDBY', 'ONGOING', 'HALT'],
        machine__owner=request.user
    ).values_list('machine_id', flat=True).distinct()
    
    # Cálculo dos 3 contadores solicitados
    active_productions_count = productions.filter(status='ONGOING').count()
    machines_used_count = user_machines.filter(id__in=busy_ids).count()
    machines_available_count = user_machines.exclude(id__in=busy_ids).count()
    
    context = {
        'productions': productions,
        'active_count': active_productions_count,
        'machines_used': machines_used_count,
        'machines_available': machines_available_count,
    }
    return render(request, 'dashboard.html', context)

@login_required
def machine_create(request):
    # Regra de negócio: limite baseado no status premium
    limit = 10 if request.user.is_premium else 5
    if Machine.objects.filter(owner=request.user).count() >= limit:
        messages.error(request, f"Limite de {limit} máquinas atingido para seu plano.")
        return redirect('dashboard')

    if request.method == 'POST':
        serial = request.POST['serialnumber']
        if Machine.all_objects.filter(serialnumber=serial).exists():
            messages.error(request, "Número de série já cadastrado no sistema.")
        else:
            Machine.objects.create(
                model=request.POST['model'],
                serialnumber=serial,
                owner=request.user
            )
            return redirect('dashboard')
    return render(request, 'machine_form.html')

@login_required
def production_create(request):
    # Máquinas disponíveis para nova produção
    busy_ids = ProductionMachine.objects.filter(
        production__status__in=['STANDBY', 'ONGOING'],
        status__in=['STANDBY', 'ONGOING', 'HALT']
    ).values_list('machine_id', flat=True)
    
    available_machines = Machine.objects.filter(owner=request.user).exclude(id__in=busy_ids)

    if request.method == 'POST':
        machine_ids = request.POST.getlist('machines')
        if not machine_ids:
            messages.error(request, "Selecione ao menos uma máquina para iniciar a produção.")
        else:
            prod = Production.objects.create(
                description=request.POST['description'],
                quantity=request.POST['quantity'],
                user=request.user
            )
            for m_id in machine_ids:
                m = get_object_or_404(Machine, id=m_id, owner=request.user)
                ProductionMachine.objects.create(production=prod, machine=m)
            return redirect('dashboard')
            
    return render(request, 'production_form.html', {'machines': available_machines})

@login_required
def update_status(request, pk, target, status):
    now = timezone.now()
    
    if target == 'production':
        prod = get_object_or_404(Production, pk=pk, user=request.user)
        
        if status == 'ONGOING':
            prod.started_at = now
            prod.status = 'ONGOING'
            prod.save()
            # Inicia todas as máquinas vinculadas que não foram canceladas
            for pm in prod.productionmachine_set.all():
                pm.status = 'ONGOING'
                pm.started_at = now
                pm.save()
                
        elif status == 'FINISHED':
            # Bloqueio: Não finaliza produção se houver máquinas operando
            if prod.productionmachine_set.filter(status__in=['STANDBY', 'ONGOING', 'HALT']).exists():
                messages.error(request, "Finalize o status de todas as máquinas individualmente antes de encerrar a produção.")
                return redirect('dashboard')
            prod.finished_at = now
            prod.status = 'FINISHED'
            prod.save()

        elif status == 'CANCELED':
            prod.canceled_at = now
            prod.status = 'CANCELED'
            prod.save()
            # Cancela máquinas que ainda estavam pendentes ou em curso
            for pm in prod.productionmachine_set.exclude(status__in=['FINISHED', 'CANCELED']):
                pm.status = 'CANCELED'
                pm.canceled_at = now
                pm.save()

    elif target == 'machine':
        pm = get_object_or_404(ProductionMachine, pk=pk, production__user=request.user)
        pm.status = status
        if status == 'FINISHED':
            pm.finished_at = now
        elif status == 'CANCELED':
            pm.canceled_at = now
        # O cálculo de working_time ocorre no save() do model ProductionMachine
        pm.save()

    return redirect('dashboard')

@login_required
def toggle_theme(request):
    user = request.user
    user.theme_mode = 'dark' if user.theme_mode == 'light' else 'light'
    user.save()
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))