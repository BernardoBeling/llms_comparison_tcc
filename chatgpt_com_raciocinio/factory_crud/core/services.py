from django.db.models import Q, Subquery
from .models import Machine, Production, ProductionMachine, ProductionStatus


def get_available_machines_for_user(user):
    """
    Regra de negócio:
    - só máquinas do usuário
    - não pode selecionar máquina que já esteja vinculada a outra produção
      que ainda não foi finalizada ou cancelada (status STANDBY/ONGOING)
    """
    active_production_ids = Production.objects.filter(
        status__in=[ProductionStatus.STANDBY, ProductionStatus.ONGOING]
    ).values("id")

    busy_machine_ids = ProductionMachine.objects.filter(
        production_id__in=Subquery(active_production_ids),
    ).values("machine_id")

    return Machine.objects.filter(owner_user=user).exclude(id__in=Subquery(busy_machine_ids))


def get_machine_counts_for_dashboard(user):
    available = get_available_machines_for_user(user).count()

    active_production_ids = Production.objects.filter(
        user=user,
        status__in=[ProductionStatus.STANDBY, ProductionStatus.ONGOING],
    ).values("id")

    used = ProductionMachine.objects.filter(production_id__in=Subquery(active_production_ids)).count()

    total = Machine.objects.filter(owner_user=user).count()

    return {
        "total": total,
        "available": available,
        "used": used,
    }
