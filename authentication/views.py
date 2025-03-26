# # authentication/views.py

# from django.shortcuts import render, redirect
# from django.contrib.auth import authenticate, login, logout
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from django.utils import timezone
# from .forms import CustomAuthenticationForm, PasswordResetRequestForm
# from .models import LoginLog, UserProfile
# from ambassadeurs.models import Ambassadeur

# def login_view(request):
#     """
#     Vue pour gérer la connexion des utilisateurs
#     """
#     # Rediriger l'utilisateur s'il est déjà connecté
#     if request.user.is_authenticated:
#         return redirect('dashboard')
    
#     if request.method == 'POST':
#         form = CustomAuthenticationForm(request, data=request.POST)
        
#         if form.is_valid():
#             username = form.cleaned_data.get('username')
#             password = form.cleaned_data.get('password')
#             user = authenticate(username=username, password=password)
            
#             if user is not None:
#                 login(request, user)
                
#                 # Enregistrer la connexion
#                 ip_address = request.META.get('REMOTE_ADDR')
#                 user_agent = request.META.get('HTTP_USER_AGENT')
                
#                 # Créer un log de connexion
#                 LoginLog.objects.create(
#                     user=user,
#                     ip_address=ip_address,
#                     user_agent=user_agent,
#                     is_successful=True
#                 )
                
#                 # Mettre à jour le profil utilisateur
#                 profile, created = UserProfile.objects.get_or_create(user=user)
#                 profile.last_login_ip = ip_address
#                 profile.save()
                
#                 # Vérifier si l'utilisateur est un ambassadeur ou un administrateur
#                 try:
#                     ambassadeur = Ambassadeur.objects.get(user=user)
#                     # Rediriger vers le tableau de bord des ambassadeurs
#                     return redirect('dashboard')
#                 except Ambassadeur.DoesNotExist:
#                     # Vérifier si c'est un administrateur
#                     if user.is_staff or getattr(profile, 'is_admin', False):
#                         return redirect('backoffice:dashboard')
#                     else:
#                         # Utilisateur non autorisé
#                         messages.error(request, "Vous n'êtes pas autorisé à accéder à cette application.")
#                         logout(request)
#                         return redirect('login')
#             else:
#                 # Créer un log d'échec de connexion
#                 LoginLog.objects.create(
#                     user=user,
#                     ip_address=request.META.get('REMOTE_ADDR'),
#                     user_agent=request.META.get('HTTP_USER_AGENT'),
#                     is_successful=False
#                 )
                
#                 messages.error(request, "Identifiant ou mot de passe invalide.")
#     else:
#         form = CustomAuthenticationForm()
    
#     return render(request, 'authentication/login.html', {'form': form})

# def logout_view(request):
#     """
#     Vue pour gérer la déconnexion des utilisateurs
#     """
#     logout(request)
#     messages.success(request, "Vous avez été déconnecté avec succès.")
#     return redirect('login')

# def password_reset_request(request):
#     """
#     Vue pour gérer les demandes de réinitialisation de mot de passe
#     """
#     if request.method == 'POST':
#         form = PasswordResetRequestForm(request.POST)
#         if form.is_valid():
#             email = form.cleaned_data.get('email')
#             # Ici, vous implémenteriez la logique pour envoyer un e-mail de réinitialisation
#             # Pour le moment, on affiche simplement un message de succès
#             messages.success(request, "Un e-mail a été envoyé à l'adresse fournie avec les instructions pour réinitialiser votre mot de passe.")
#             return redirect('login')
#     else:
#         form = PasswordResetRequestForm()
    
#     return render(request, 'authentication/password_reset_request.html', {'form': form})

# @login_required
# def profile_view(request):
#     """
#     Vue pour afficher et modifier le profil de l'utilisateur
#     """
#     try:
#         ambassadeur = Ambassadeur.objects.get(user=request.user)
#         return render(request, 'authentication/profile.html', {'ambassadeur': ambassadeur})
#     except Ambassadeur.DoesNotExist:
#         messages.error(request, "Vous n'êtes pas enregistré comme ambassadeur.")
#         return redirect('login')


# authentication/views.py (version simplifiée)

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .forms import CustomAuthenticationForm
from ambassadeurs.models import Ambassadeur

def login_view(request):
    """
    Vue simplifiée pour la connexion sans AD
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = CustomAuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            
            if user is not None:
                login(request, user)
                
                # Pour les tests, on vérifie si c'est un admin ou un ambassadeur
                if user.is_staff:
                    return redirect('backoffice:dashboard')
                
                # Vérifier si l'utilisateur est un ambassadeur
                try:
                    ambassadeur = Ambassadeur.objects.get(user=user)
                    return redirect('dashboard')
                except Ambassadeur.DoesNotExist:
                    # Si l'utilisateur n'est ni admin ni ambassadeur
                    messages.error(request, "Vous n'êtes pas autorisé à accéder à cette application.")
                    logout(request)
            else:
                messages.error(request, "Identifiant ou mot de passe invalide.")
    else:
        form = CustomAuthenticationForm()
    
    return render(request, 'authentication/login.html', {'form': form})

@login_required
def association_code(request):
    """
    Vue pour associer un utilisateur à son code ambassadeur
    """
    # Vérifier si l'utilisateur est déjà associé à un ambassadeur
    if Ambassadeur.objects.filter(user=request.user).exists():
        return redirect('dashboard')
    
    if request.method == 'POST':
        code_ambassadeur = request.POST.get('code_ambassadeur')
        
        try:
            # Trouver l'ambassadeur avec ce code et sans utilisateur associé
            ambassadeur = Ambassadeur.objects.get(code_ambassadeur=code_ambassadeur, user__isnull=True)
            
            # Associer l'utilisateur à l'ambassadeur
            ambassadeur.user = request.user
            ambassadeur.email = request.user.email
            ambassadeur.nom_complet = f"{request.user.first_name} {request.user.last_name}"
            ambassadeur.save()
            
            messages.success(request, "Votre compte a été associé avec succès à votre code ambassadeur.")
            return redirect('dashboard')
        
        except Ambassadeur.DoesNotExist:
            messages.error(request, "Ce code ambassadeur n'existe pas ou est déjà associé à un autre utilisateur.")
    
    return render(request, 'authentication/association_code.html')

def logout_view(request):
    """
    Vue pour la déconnexion
    """
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès.")
    return redirect('home')  # Rediriger vers la landing page

@login_required
def profile_view(request):
    """
    Vue simplifiée pour le profil
    """
    try:
        ambassadeur = Ambassadeur.objects.get(user=request.user)
        return render(request, 'authentication/profile.html', {'ambassadeur': ambassadeur})
    except Ambassadeur.DoesNotExist:
        return render(request, 'authentication/profile.html')