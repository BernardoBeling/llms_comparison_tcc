from django.urls import path
from .views import (
    DashboardView,
    MachineListView,
    MachineCreateView,
    ProductionListView,
    ProductionCreateView,
    ProductionDetailView,
    start_production,
    cancel_production,
    finish_production,
    cancel_production_machine,
    finish_production_machine,
    set_theme,
)

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),

    path("machines/", MachineListView.as_view(), name="machine_list"),
    path("machines/new/", MachineCreateView.as_view(), name="machine_create"),

    path("productions/", ProductionListView.as_view(), name="production_list"),
    path("productions/new/", ProductionCreateView.as_view(), name="production_create"),
    path("productions/<int:pk>/", ProductionDetailView.as_view(), name="production_detail"),

    path("productions/<int:pk>/start/", start_production, name="production_start"),
    path("productions/<int:pk>/cancel/", cancel_production, name="production_cancel"),
    path("productions/<int:pk>/finish/", finish_production, name="production_finish"),

    path("productions/<int:pk>/machines/<int:pm_id>/cancel/", cancel_production_machine, name="production_machine_cancel"),
    path("productions/<int:pk>/machines/<int:pm_id>/finish/", finish_production_machine, name="production_machine_finish"),

    # ✅ tema
    path("theme/<str:mode>/", set_theme, name="set_theme"),
]
