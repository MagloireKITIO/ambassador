# ambassadeurs/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('historique/points/', views.historique_points, name='historique_points'),
    path('historique/polices/', views.historique_polices, name='historique_polices'),
    path('historique/echanges/', views.historique_echanges, name='historique_echanges'),
    path('historique/points/export/', views.exporter_historique_points, name='exporter_historique_points'),
    path('historique/polices/export/', views.exporter_historique_polices, name='exporter_historique_polices'),
    path('historique/echanges/export/', views.exporter_historique_echanges, name='exporter_historique_echanges'),

]