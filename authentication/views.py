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
    Vue simplifiée pour la connexion
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
                if Ambassadeur.objects.filter(user=user).exists():
                    return redirect('dashboard')
                else:
                    # Au lieu de déconnecter, rediriger vers l'association de code
                    return redirect('association_code')
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
        type_ambassadeur = request.POST.get('type_ambassadeur')
        code_ambassadeur_vie = request.POST.get('code_ambassadeur_vie')
        code_ambassadeur_non_vie = request.POST.get('code_ambassadeur_non_vie')
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        date_naissance = request.POST.get('date_naissance')
        telephone = request.POST.get('telephone')
        email = request.POST.get('email', request.user.email)
        
        # Vérifications de base
        if not type_ambassadeur or (type_ambassadeur == 'vie' and not code_ambassadeur_vie) or (type_ambassadeur == 'non_vie' and not code_ambassadeur_non_vie) or (type_ambassadeur == 'les_deux' and (not code_ambassadeur_vie or not code_ambassadeur_non_vie)) or not nom or not prenom:
            messages.error(request, "Veuillez remplir tous les champs obligatoires.")
            return render(request, 'authentication/association_code.html', {'type_ambassadeur': type_ambassadeur})
        
        # Vérifier que les codes n'existent pas déjà
        if code_ambassadeur_vie and Ambassadeur.objects.filter(code_ambassadeur_vie=code_ambassadeur_vie).exists():
            messages.error(request, "Ce code ambassadeur Vie est déjà utilisé.")
            return render(request, 'authentication/association_code.html', {'type_ambassadeur': type_ambassadeur})
        
        if code_ambassadeur_non_vie and Ambassadeur.objects.filter(code_ambassadeur_non_vie=code_ambassadeur_non_vie).exists():
            messages.error(request, "Ce code ambassadeur Non-Vie est déjà utilisé.")
            return render(request, 'authentication/association_code.html', {'type_ambassadeur': type_ambassadeur})
        
        try:
            # Créer un nouvel ambassadeur
            nom_complet = f"{prenom} {nom}"
            
            ambassadeur = Ambassadeur.objects.create(
                user=request.user,
                type_ambassadeur=type_ambassadeur,
                code_ambassadeur_vie=code_ambassadeur_vie if type_ambassadeur in ['vie', 'les_deux'] else None,
                code_ambassadeur_non_vie=code_ambassadeur_non_vie if type_ambassadeur in ['non_vie', 'les_deux'] else None,
                nom_complet=nom_complet,
                date_naissance=date_naissance if date_naissance else None,
                telephone=telephone,
                email=email,
                actif=True
            )
            
            messages.success(request, "Votre compte a été créé avec succès. Bienvenue dans le programme Ambassadeurs!")
            return redirect('dashboard')
        
        except Exception as e:
            messages.error(request, f"Une erreur s'est produite: {str(e)}")
    
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