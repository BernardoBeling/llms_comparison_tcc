from django.urls import path

from .views import AppLoginView, AppLogoutView, SignupView

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', AppLoginView.as_view(), name='login'),
    path('logout/', AppLogoutView.as_view(), name='logout'),
]
