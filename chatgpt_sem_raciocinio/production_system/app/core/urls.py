from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('signup/', views.signup, name='signup'),
    path('machines/', views.machines, name='machines'),
    path('productions/', views.productions, name='productions'),
    path('productions/<int:id>/cancel/', views.cancel_production, name='cancel_production'),
    path('production-machine/<int:pm_id>/cancel/', views.cancel_machine, name='cancel_machine'),
    path('production-machine/<int:pm_id>/finish/', views.finish_machine, name='finish_machine'),
    path('productions/<int:id>/finish/', views.finish_production, name='finish_production'),
    path('toggle-theme/', views.toggle_theme, name='toggle_theme'),
    path(
        'production-machine/<int:pk>/cancel/',
        views.cancel_production_machine,
        name='cancel_production_machine'
    ),
    path(
        'production-machine/<int:pk>/finish/',
        views.finish_production_machine,
        name='finish_production_machine'
    ),
    path('production/<int:pk>/cancel/', views.cancel_production, name='cancel_production'),
path('production/<int:pk>/finish/', views.finish_production, name='finish_production'),
path(
    'production-machine/<int:pm_id>/start/',
    views.start_machine,
    name='start_machine'
),
]
