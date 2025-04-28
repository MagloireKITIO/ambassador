# # backoffice/urls.py

# from django.urls import path
# from . import views

# app_name = 'backoffice'

# urlpatterns = [
#     path('', views.dashboard, name='dashboard'),
#     path('ambassadeurs/', views.gestion_ambassadeurs, name='gestion_ambassadeurs'),
#     path('recompenses/', views.gestion_recompenses, name='gestion_recompenses'),
#     path('echanges/', views.gestion_echanges, name='gestion_echanges'),
#     path('echanges/valider/<int:echange_id>/', views.valider_echange, name='valider_echange'),
#     path('configuration/', views.configuration_systeme, name='configuration_systeme'),
#     path('exercices/', views.gestion_exercices, name='gestion_exercices'),
    
#     # URLs pour l'import
#     path('import/', views.importer_donnees, name='importer_donnees'),
#     path('import/polices-vie/', views.import_polices_vie, name='import_polices_vie'),
#     path('import/polices-non-vie/', views.import_polices_non_vie, name='import_polices_non_vie'),
#     path('import/logs/', views.import_logs, name='import_logs'),
    
#     path('rapports/points/', views.rapport_points, name='rapport_points'),
#     path('ambassadeurs/', views.gestion_codes_ambassadeurs, name='gestion_codes_ambassadeurs'),
#     path('ambassadeurs/ajouter/', views.ajouter_code_ambassadeur, name='ajouter_code_ambassadeur'),
#     path('ambassadeurs/dissocier/<int:ambassadeur_id>/', views.dissocier_ambassadeur, name='dissocier_ambassadeur'),
#     path('ambassadeurs/modifier/<int:ambassadeur_id>/', views.modifier_ambassadeur, name='modifier_ambassadeur'),
#     path('ambassadeurs/detail/<int:ambassadeur_id>/', views.detail_ambassadeur, name='detail_ambassadeur'),
# ]

# backoffice/urls.py

from django.urls import path
from . import views

app_name = 'backoffice'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('import/', views.importer_donnees, name='importer_donnees'),
    path('import/vie/', views.import_polices_vie, name='import_polices_vie'),
    path('import/non-vie/', views.import_polices_non_vie, name='import_polices_non_vie'),
    path('import/polices/', views.import_polices, name='import_polices'),
    path('import/logs/', views.import_logs, name='import_logs'),
    
    # Ambassadeurs
    path('ambassadeurs/', views.gestion_ambassadeurs, name='gestion_ambassadeurs'),
    path('ambassadeurs/codes/', views.gestion_codes_ambassadeurs, name='gestion_codes_ambassadeurs'),
    path('ambassadeurs/codes/ajouter/', views.ajouter_code_ambassadeur, name='ajouter_code_ambassadeur'),
    path('ambassadeurs/<int:ambassadeur_id>/', views.detail_ambassadeur, name='detail_ambassadeur'),
    path('ambassadeurs/<int:ambassadeur_id>/modifier/', views.modifier_ambassadeur, name='modifier_ambassadeur'),
    path('ambassadeurs/<int:ambassadeur_id>/dissocier/', views.dissocier_ambassadeur, name='dissocier_ambassadeur'),
    
    # Récompenses
    path('recompenses/', views.gestion_recompenses, name='gestion_recompenses'),
    path('recompenses/ajouter/', views.ajouter_recompense, name='ajouter_recompense'),
    path('recompenses/<int:recompense_id>/modifier/', views.modifier_recompense, name='modifier_recompense'),
    path('recompenses/<int:recompense_id>/activer/', views.activer_recompense, name='activer_recompense'),
    path('recompenses/<int:recompense_id>/desactiver/', views.desactiver_recompense, name='desactiver_recompense'),
    
    # Échanges
    path('echanges/', views.gestion_echanges, name='gestion_echanges'),
    path('echanges/export/', views.exporter_echanges, name='exporter_echanges'),
    path('echanges/<int:echange_id>/', views.detail_echange, name='detail_echange'),
    path('echanges/<int:echange_id>/valider/', views.valider_echange, name='valider_echange'),
    path('echanges/<int:echange_id>/expedier/', views.expedier_echange, name='expedier_echange'),
    path('echanges/<int:echange_id>/livrer/', views.livrer_echange, name='livrer_echange'),
    path('echanges/<int:echange_id>/annuler/', views.annuler_echange, name='annuler_echange'),
    path('echanges/<int:echange_id>/commentaire/', views.ajouter_commentaire, name='ajouter_commentaire'),
    path('echanges/<int:echange_id>/notification/', views.envoyer_notification, name='envoyer_notification'),
    
    # Configuration
    path('configuration/', views.configuration_systeme, name='configuration_systeme'),
    path('exercices/', views.gestion_exercices, name='gestion_exercices'),
    path('exercices/ajouter/', views.ajouter_exercice, name='ajouter_exercice'),
    path('exercices/<int:exercice_id>/modifier/', views.modifier_exercice, name='modifier_exercice'),
    path('exercices/<int:exercice_id>/activer/', views.activer_exercice, name='activer_exercice'),
    path('exercices/<int:exercice_id>/desactiver/', views.desactiver_exercice, name='desactiver_exercice'),
    
    # Rapports
    path('rapports/points/', views.rapport_points, name='rapport_points'),

    # Section profil administrateur
    path('profil/', views.profil_admin, name='profil_admin'),
    path('profil/modifier/', views.modifier_profil, name='modifier_profil'),
    path('profil/changer-mot-de-passe/', views.changer_mot_de_passe, name='changer_mot_de_passe'),

    # Catégories
    path('categories/', views.gestion_categories, name='gestion_categories'),

    # Gestion des administrateurs
    path('admins/', views.gestion_admins, name='gestion_admins'),
    path('admins/ajouter/', views.ajouter_admin, name='ajouter_admin'),
    path('admins/<int:admin_id>/modifier/', views.modifier_admin, name='modifier_admin'),
    path('admins/<int:admin_id>/activer/', views.activer_admin, name='activer_admin'),
    path('admins/<int:admin_id>/desactiver/', views.desactiver_admin, name='desactiver_admin'),
    # path('admins/<int:admin_id>/reinitialiser-mdp/', views.reinitialiser_mdp_admin, name='reinitialiser_mdp_admin'),
]