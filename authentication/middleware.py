# Mise à jour du middleware dans authentication/middleware.py

from django.shortcuts import redirect
from django.urls import resolve, reverse
from django.contrib import messages
from ambassadeurs.models import Ambassadeur

class AmbassadeurCheckMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Vérifier si l'utilisateur est authentifié
        if request.user.is_authenticated:
            # Vérifier si l'utilisateur est un admin ou a un profil d'admin
            if request.user.is_staff or (hasattr(request.user, 'profile') and request.user.profile.is_admin):
                # Les admins n'ont pas besoin d'avoir un profil ambassadeur
                pass
            else:
                # Vérifier si l'URL actuelle n'est pas déjà la page d'association ou liée à l'authentification
                try:
                    current_url = resolve(request.path_info).url_name
                    current_namespace = resolve(request.path_info).namespace
                    
                    # Liste des URLs à exclure de la redirection
                    excluded_urls = ['association_code', 'logout', 'login']
                    
                    # Si l'URL fait partie de l'authentification sociale, on l'exclut également
                    if current_namespace == 'social' or current_url in excluded_urls:
                        pass
                    else:
                        # Vérifier si l'utilisateur a un profil ambassadeur
                        if not Ambassadeur.objects.filter(user=request.user).exists():
                            # Redirection vers la page d'association
                            return redirect('association_code')
                except Exception as e:
                    # En cas d'erreur, loggez-la pour déboguer
                    print(f"Erreur dans AmbassadeurCheckMiddleware: {str(e)}")
        
        response = self.get_response(request)
        return response