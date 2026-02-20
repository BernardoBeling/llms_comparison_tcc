from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import Machine, Production, ProductionMachine
from .forms import MachineForm, ProductionForm, UserRegisterForm
from django.contrib.auth import login
from django.db.models import Q

@login_required
def dashboard(request):
    user = request.user

    # productions = Production.objects.filter(user=user)
    productions = (
    Production.objects
    .filter(user=request.user)
    .prefetch_related('productionmachine_set__machine')
)

    # Máquinas do usuário
    all_machines = Machine.objects.filter(owner_user=user)


    # Máquinas em produções ativas (STANDBY ou ONGOING)
    used_machine_ids = ProductionMachine.objects.filter(
        production__status__in=['STANDBY', 'ONGOING'],
        machine__owner_user=user
    ).values_list('machine_id', flat=True)

    used_machines_count = all_machines.filter(
        id__in=used_machine_ids
    ).count()

    available_machines_count = all_machines.exclude(
        id__in=used_machine_ids
    ).count()

    ongoing_productions_count = productions.filter(
        status='ONGOING'
    ).count()

    return render(request, 'dashboard.html', {
        'productions': productions,
        'ongoing_productions_count': ongoing_productions_count,
        'used_machines_count': used_machines_count,
        'available_machines_count': available_machines_count,
    })

# @login_required
# def machines(request):
#     if request.method == 'POST':
#         if Machine.objects.filter(owner_user=request.user).count() >= 5:
#             return redirect('machines')

#         form = MachineForm(request.POST or None, user=request.user)
#         if form.is_valid():
#             machine = form.save(commit=False)
#             machine.owner_user = request.user
#             machine.save()
#             return redirect('machines')
#     else:
#         form = MachineForm(user=request.user)


#     return render(request, 'machines.html', {
#         'form': form,
#         'machines': Machine.objects.filter(owner_user=request.user)
#     })

@login_required
def machines(request):
    if request.method == 'POST':
        form = MachineForm(request.POST, user=request.user)
        if form.is_valid():
            machine = form.save(commit=False)
            machine.owner_user = request.user
            machine.save()
            return redirect('machines')
    else:
        form = MachineForm(user=request.user)

    machines = Machine.objects.filter(owner_user=request.user)
    return render(request, 'machines.html', {
        'form': form,
        'machines': machines
    })

@login_required
def productions(request):
    if request.method == 'POST':
        form = ProductionForm(request.POST, user=request.user)
        if form.is_valid():
            production = form.save(commit=False)
            production.user = request.user
            production.status = 'STANDBY'
            production.save()

            for machine in form.cleaned_data['machines']:
                ProductionMachine.objects.create(
                    production=production,
                    machine=machine,
                    status='STANDBY'
                )

            return redirect('dashboard')
    else:
        form = ProductionForm(user=request.user)

    return render(request, 'productions.html', {'form': form})

# @login_required
# def cancel_production(request, id):
#     production = get_object_or_404(Production, id=id, user=request.user)
#     production.status = 'CANCELED'
#     production.canceled_at = timezone.now()
#     production.save()

#     ProductionMachine.objects.filter(production=production).update(
#         status='CANCELED',
#         canceled_at=timezone.now()
#     )

#     return redirect('dashboard')

@login_required
def cancel_production(request, pk):
    production = get_object_or_404(Production, pk=pk, user=request.user)
    production.cancel()
    return redirect('dashboard')

def signup(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.email
            user.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserRegisterForm()

    return render(request, 'signup.html', {'form': form})

@login_required
def cancel_machine(request, pm_id):
    pm = get_object_or_404(
        ProductionMachine,
        id=pm_id,
        production__user=request.user
    )

    pm.cancel()                 # 🔥 regra centralizada
    pm.production.try_finish()  # 🔥 verifica produção

    return redirect('dashboard')

@login_required
def finish_machine(request, pm_id):
    pm = get_object_or_404(
        ProductionMachine,
        id=pm_id,
        production__user=request.user
    )

    pm.finish()
    pm.production.try_finish()

    return redirect('dashboard')

# @login_required
# def finish_production(request, id):
#     production = get_object_or_404(
#         Production,
#         id=id,
#         user=request.user
#     )

#     invalid_machines = ProductionMachine.objects.filter(
#         production=production,
#         status__in=['STANDBY', 'ONGOING']
#     )

#     if not invalid_machines.exists():
#         production.status = 'FINISHED'
#         production.finished_at = timezone.now()
#         production.save()

#     return redirect('dashboard')

@login_required
def finish_production(request, pk):
    production = get_object_or_404(Production, pk=pk, user=request.user)
    production.try_finish()
    return redirect('dashboard')

@login_required
def toggle_theme(request):
    current = request.session.get('theme', 'light')
    request.session['theme'] = 'dark' if current == 'light' else 'light'
    return redirect(request.META.get('HTTP_REFERER', 'dashboard'))

# @login_required
# def cancel_production_machine(request, pk):
#     pm = get_object_or_404(ProductionMachine, pk=pk)

#     # segurança básica
#     if pm.machine.owner_user != request.user:
#         return redirect('dashboard')

#     if pm.status not in ['FINISHED', 'CANCELED']:
#         pm.status = 'CANCELED'
#         pm.canceled_at = timezone.now()
#         pm.save()

#     return redirect('dashboard')

@login_required
def cancel_production_machine(request, pk):
    pm = get_object_or_404(ProductionMachine, pk=pk)

    if pm.machine.owner_user != request.user:
        return redirect('dashboard')

    pm.cancel()
    pm.production.try_finish()
    return redirect('dashboard')


# @login_required
# def finish_production_machine(request, pk):
#     pm = get_object_or_404(ProductionMachine, pk=pk)

#     if pm.machine.owner_user != request.user:
#         return redirect('dashboard')

#     if pm.status not in ['FINISHED', 'CANCELED']:
#         pm.status = 'FINISHED'
#         pm.finished_at = timezone.now()
#         pm.save()

#     # verificar se a produção pode ser finalizada
#     production = pm.production
#     remaining = production.productionmachine_set.filter(
#         status__in=['STANDBY', 'ONGOING']
#     ).exists()

#     if not remaining:
#         production.status = 'FINISHED'
#         production.finished_at = timezone.now()
#         production.save()

#     return redirect('dashboard')

@login_required
def finish_production_machine(request, pk):
    pm = get_object_or_404(ProductionMachine, pk=pk)

    if pm.machine.owner_user != request.user:
        return redirect('dashboard')

    pm.finish()
    pm.production.try_finish()
    return redirect('dashboard')

@login_required
def start_machine(request, pm_id):
    pm = get_object_or_404(
        ProductionMachine,
        id=pm_id,
        production__user=request.user
    )

    if pm.status == 'STANDBY':
        pm.status = 'ONGOING'
        pm.started_at = timezone.now()
        pm.save()

    return redirect('dashboard')