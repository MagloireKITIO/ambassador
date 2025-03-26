# backoffice/urls.py

from django.urls import path
from . import views

app_name = 'backoffice'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('ambassadeurs/', views.gestion_ambassadeurs, name='gestion_ambassadeurs'),
    path('recompenses/', views.gestion_recompenses, name='gestion_recompenses'),
    path('echanges/', views.gestion_echanges, name='gestion_echanges'),
    path('echanges/valider/<int:echange_id>/', views.valider_echange, name='valider_echange'),
    path('configuration/', views.configuration_systeme, name='configuration_systeme'),
    path('exercices/', views.gestion_exercices, name='gestion_exercices'),
    path('import/', views.importer_donnees, name='importer_donnees'),
    path('rapports/points/', views.rapport_points, name='rapport_points'),
     path('codes-ambassadeurs/', views.gestion_codes_ambassadeurs, name='gestion_codes_ambassadeurs'),
    path('codes-ambassadeurs/ajouter/', views.ajouter_code_ambassadeur, name='ajouter_code_ambassadeur'),
    path('codes-ambassadeurs/dissocier/<int:ambassadeur_id>/', views.dissocier_code_ambassadeur, name='dissocier_code_ambassadeur'),
]