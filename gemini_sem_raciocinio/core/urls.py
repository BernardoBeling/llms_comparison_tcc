from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('machine/new/', views.machine_create, name='machine_create'),
    path('production/new/', views.production_create, name='production_create'),
    path('production/<int:pk>/', views.production_detail, name='production_detail'),
    path('production/<int:pk>/cancel/', views.production_cancel, name='production_cancel'),
    path('production/<int:pk>/finish/', views.production_finish, name='production_finish'),
    path('production-machine/<int:pk>/cancel/', views.machine_cancel, name='machine_cancel'),
    path('production-machine/<int:pk>/finish/', views.machine_finish, name='machine_finish'), # Nova Rota
]