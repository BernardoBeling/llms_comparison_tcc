from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),  # Corrigido: removido o '.py'
    path('', include('core.urls')),
    path('accounts/', include('django.contrib.auth.urls')), # Provê login/logout nativo
]