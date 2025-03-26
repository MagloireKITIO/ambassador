# authentication/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('association-code/', views.association_code, name='association_code'),
    # path('password-reset/', views.password_reset_request, name='password_reset_request'),
    # path('profile/', views.profile_view, name='profile'),
]