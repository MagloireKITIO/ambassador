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
    
    # URLs pour l'import
    path('import/', views.importer_donnees, name='importer_donnees'),
    path('import/polices-vie/', views.import_polices_vie, name='import_polices_vie'),
    path('import/polices-non-vie/', views.import_polices_non_vie, name='import_polices_non_vie'),
    path('import/logs/', views.import_logs, name='import_logs'),
    
    path('rapports/points/', views.rapport_points, name='rapport_points'),
    path('ambassadeurs/', views.gestion_codes_ambassadeurs, name='gestion_codes_ambassadeurs'),
    path('ambassadeurs/ajouter/', views.ajouter_code_ambassadeur, name='ajouter_code_ambassadeur'),
    path('ambassadeurs/dissocier/<int:ambassadeur_id>/', views.dissocier_ambassadeur, name='dissocier_ambassadeur'),
    path('ambassadeurs/modifier/<int:ambassadeur_id>/', views.modifier_ambassadeur, name='modifier_ambassadeur'),
    path('ambassadeurs/detail/<int:ambassadeur_id>/', views.detail_ambassadeur, name='detail_ambassadeur'),
]