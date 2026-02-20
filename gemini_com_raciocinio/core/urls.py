from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('machines/new/', views.machine_create, name='machine_create'),
    path('productions/new/', views.production_create, name='production_create'),
    path('update/<int:pk>/<str:target>/<str:status>/', views.update_status, name='update'),
    path('theme/toggle/', views.toggle_theme, name='toggle_theme'), # Rota para o Tema
]