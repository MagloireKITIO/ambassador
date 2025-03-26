# activa_ambassadeurs/urls.py

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),  # Admin Django par défaut
    path('', TemplateView.as_view(template_name='landing_page.html'), name='home'),  # Landing page
    path('auth/', include('authentication.urls')),
    path('dashboard/', include('ambassadeurs.urls')),
    path('rewards/', include('rewards.urls')),
    path('backoffice/', include('backoffice.urls')),
    path('api/', include('rest_framework.urls')),
]

# Servir les fichiers media en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)