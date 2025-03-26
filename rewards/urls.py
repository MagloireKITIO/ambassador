# rewards/urls.py

from django.urls import path
from . import views

urlpatterns = [
    path('catalogue/', views.catalogue, name='catalogue'),
    path('recompense/<int:recompense_id>/', views.detail_recompense, name='detail_recompense'),
    path('echanger/<int:recompense_id>/', views.echanger_recompense, name='echanger_recompense'),
    path('annuler-echange/<int:echange_id>/', views.annuler_echange, name='annuler_echange'),
    path('api/verifier-points/', views.verifier_points, name='verifier_points'),
]