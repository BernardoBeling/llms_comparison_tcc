from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse
from django.views.generic import ListView, CreateView, DetailView
from django.utils.decorators import method_decorator

from .models import (
    Machine,
    Production,
    ProductionMachine,
    ProductionStatus,
    ProductionMachineStatus,
)
from .forms import MachineForm, ProductionCreateForm
from .services import get_machine_counts_for_dashboard


@method_decorator(login_required, name="dispatch")
class DashboardView(ListView):
    template_name = "dashboard.html"
    model = Production
    context_object_name = "productions"

    def get_queryset(self):
        return Production.objects.filter(user=self.request.user).order_by("-created_at")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ongoing_count = Production.objects.filter(user=self.request.user, status=ProductionStatus.ONGOING).count()
        counts = get_machine_counts_for_dashboard(self.request.user)

        ctx["ongoing_count"] = ongoing_count
        ctx["machine_total"] = counts["total"]
        ctx["machine_used"] = counts["used"]
        ctx["machine_available"] = counts["available"]
        return ctx


@method_decorator(login_required, name="dispatch")
class MachineListView(ListView):
    template_name = "machines/machine_list.html"
    model = Machine
    context_object_name = "machines"

    def get_queryset(self):
        return Machine.objects.filter(owner_user=self.request.user).order_by("-created_at")


@method_decorator(login_required, name="dispatch")
class MachineCreateView(CreateView):
    template_name = "machines/machine_form.html"
    model = Machine
    form_class = MachineForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["owner_user"] = self.request.user
        return kwargs

    def get_success_url(self):
        messages.success(self.request, "Máquina cadastrada com sucesso.")
        return reverse("machine_list")


@method_decorator(login_required, name="dispatch")
class ProductionListView(ListView):
    template_name = "productions/production_list.html"
    model = Production
    context_object_name = "productions"

    def get_queryset(self):
        # ✅ para mostrar working_time por máquina na lista, sem N+1
        return (
            Production.objects.filter(user=self.request.user)
            .prefetch_related("production_machines__machine")
            .order_by("-created_at")
        )


@method_decorator(login_required, name="dispatch")
class ProductionCreateView(CreateView):
    template_name = "productions/production_form.html"
    model = Production
    form_class = ProductionCreateForm

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs["user"] = self.request.user
        return kwargs

    def form_valid(self, form):
        prod = form.save()
        messages.success(self.request, f"Produção #{prod.id} cadastrada com sucesso.")
        return redirect("production_detail", pk=prod.id)


@method_decorator(login_required, name="dispatch")
class ProductionDetailView(DetailView):
    template_name = "productions/production_detail.html"
    model = Production
    context_object_name = "production"

    def get_queryset(self):
        return Production.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["machines"] = self.object.production_machines.select_related("machine").order_by("id")
        return ctx


@login_required
@transaction.atomic
def start_production(request, pk):
    production = get_object_or_404(Production, pk=pk, user=request.user)

    if production.status != ProductionStatus.STANDBY:
        messages.error(request, "A produção só pode ser iniciada se estiver em STANDBY.")
        return redirect("production_detail", pk=pk)

    production.set_status(ProductionStatus.ONGOING)

    pms = production.production_machines.all()
    for pm in pms:
        if pm.status == ProductionMachineStatus.STANDBY:
            pm.set_status(ProductionMachineStatus.ONGOING)

    messages.success(request, f"Produção #{production.id} iniciada.")
    return redirect("production_detail", pk=pk)


@login_required
@transaction.atomic
def cancel_production(request, pk):
    production = get_object_or_404(Production, pk=pk, user=request.user)

    if production.status in [ProductionStatus.FINISHED, ProductionStatus.CANCELED]:
        messages.error(request, "Não é possível cancelar uma produção finalizada ou já cancelada.")
        return redirect("production_detail", pk=pk)

    production.set_status(ProductionStatus.CANCELED)

    pms = production.production_machines.all()
    for pm in pms:
        if pm.status != ProductionMachineStatus.FINISHED and pm.status != ProductionMachineStatus.CANCELED:
            pm.set_status(ProductionMachineStatus.CANCELED)

    messages.success(request, f"Produção #{production.id} cancelada e máquinas associadas canceladas.")
    return redirect("production_detail", pk=pk)


@login_required
@transaction.atomic
def finish_production(request, pk):
    production = get_object_or_404(Production, pk=pk, user=request.user)

    if production.status in [ProductionStatus.FINISHED, ProductionStatus.CANCELED]:
        messages.error(request, "Não é possível finalizar uma produção cancelada ou já finalizada.")
        return redirect("production_detail", pk=pk)

    if not production.can_finish():
        messages.error(
            request,
            "A produção só pode ser FINALIZADA quando todas as máquinas estiverem com status diferente de STANDBY e ONGOING."
        )
        return redirect("production_detail", pk=pk)

    production.set_status(ProductionStatus.FINISHED)
    messages.success(request, f"Produção #{production.id} finalizada.")
    return redirect("production_detail", pk=pk)


@login_required
@transaction.atomic
def cancel_production_machine(request, pk, pm_id):
    production = get_object_or_404(Production, pk=pk, user=request.user)
    pm = get_object_or_404(ProductionMachine, pk=pm_id, production=production)

    if production.status in [ProductionStatus.FINISHED, ProductionStatus.CANCELED]:
        messages.error(request, "Não é possível alterar máquinas de uma produção finalizada/cancelada.")
        return redirect("production_detail", pk=pk)

    if pm.status == ProductionMachineStatus.CANCELED:
        messages.info(request, "Esta máquina já está cancelada.")
        return redirect("production_detail", pk=pk)

    if pm.status == ProductionMachineStatus.FINISHED:
        messages.error(request, "Não é possível cancelar uma máquina finalizada.")
        return redirect("production_detail", pk=pk)

    pm.set_status(ProductionMachineStatus.CANCELED)
    messages.success(request, f"Execução cancelada para a máquina {pm.machine}. A produção não foi alterada.")
    return redirect("production_detail", pk=pk)


@login_required
@transaction.atomic
def finish_production_machine(request, pk, pm_id):
    production = get_object_or_404(Production, pk=pk, user=request.user)
    pm = get_object_or_404(ProductionMachine, pk=pm_id, production=production)

    if production.status in [ProductionStatus.FINISHED, ProductionStatus.CANCELED]:
        messages.error(request, "Não é possível finalizar máquinas de uma produção finalizada/cancelada.")
        return redirect("production_detail", pk=pk)

    if production.status != ProductionStatus.ONGOING:
        messages.error(request, "Só é possível finalizar a máquina quando a produção estiver em ONGOING.")
        return redirect("production_detail", pk=pk)

    if pm.status == ProductionMachineStatus.FINISHED:
        messages.info(request, "Esta máquina já está finalizada.")
        return redirect("production_detail", pk=pk)

    if pm.status == ProductionMachineStatus.CANCELED:
        messages.error(request, "Não é possível finalizar uma máquina cancelada.")
        return redirect("production_detail", pk=pk)

    if pm.status not in [ProductionMachineStatus.ONGOING, ProductionMachineStatus.HALT]:
        messages.error(request, "Só é possível finalizar a máquina se ela estiver em ONGOING (ou HALT).")
        return redirect("production_detail", pk=pk)

    pm.set_status(ProductionMachineStatus.FINISHED)
    messages.success(request, f"Máquina {pm.machine} finalizada com sucesso.")

    if production.can_finish():
        messages.info(request, "Todas as máquinas já estão fora de STANDBY/ONGOING. Você já pode FINALIZAR a produção.")

    return redirect("production_detail", pk=pk)


def set_theme(request, mode):
    """
    ✅ Incremental: alternância Light/Dark.
    - Persistência por navegador: session + cookie.
    - Retrocompatível: não altera auth nem dados existentes.
    """
    mode = (mode or "").lower().strip()
    if mode not in ["light", "dark"]:
        mode = "light"

    request.session["ui_theme"] = mode

    resp = redirect(request.META.get("HTTP_REFERER") or "dashboard")
    resp.set_cookie("ui_theme", mode, max_age=60 * 60 * 24 * 365, samesite="Lax")
    return resp
