from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('machines/', views.machine_list, name='machine_list'),
    path('productions/new/', views.production_create, name='production_create'),
    path('productions/<int:pk>/start/', views.production_start, name='production_start'),
    path('productions/<int:pk>/cancel/', views.production_cancel, name='production_cancel'),
    path('productions/<int:pk>/finish/', views.production_finish, name='production_finish'),
    path('production-machine/<int:pm_pk>/cancel/', views.machine_cancel, name='machine_cancel'),
    path('production-machine/<int:pm_pk>/finish/', views.machine_finish, name='machine_finish'),
]
