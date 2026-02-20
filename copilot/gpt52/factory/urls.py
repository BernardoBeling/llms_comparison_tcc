from django.urls import path

from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('machines/', views.machine_list, name='machine_list'),
    path('machines/<int:machine_id>/delete/', views.machine_delete, name='machine_delete'),
    path('productions/', views.production_list, name='production_list'),
    path('productions/<int:production_id>/', views.production_detail, name='production_detail'),
    path('productions/<int:production_id>/delete/', views.production_delete, name='production_delete'),
    path('productions/<int:production_id>/start/', views.production_start, name='production_start'),
    path('productions/<int:production_id>/cancel/', views.production_cancel, name='production_cancel'),
    path('productions/<int:production_id>/finish/', views.production_finish, name='production_finish'),
    path(
        'productions/<int:production_id>/machines/<int:pm_id>/cancel/',
        views.production_machine_cancel,
        name='production_machine_cancel',
    ),
    path(
        'productions/<int:production_id>/machines/<int:pm_id>/finish/',
        views.production_machine_finish,
        name='production_machine_finish',
    ),
]
