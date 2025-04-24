# authentication/views.py

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from social_django.models import UserSocialAuth
from .forms import CustomAuthenticationForm
from ambassadeurs.models import Ambassadeur

def login_view(request):
    """
    Vue pour gérer la connexion des utilisateurs
    Note: La connexion Google est gérée directement par social-auth-app-django
    """
    # Si l'utilisateur est déjà connecté, rediriger vers le tableau de bord
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
                    # Rediriger vers l'association de code
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
    Cette vue traite également les utilisateurs connectés via Google
    """
    # Vérifier si l'utilisateur est déjà associé à un ambassadeur
    if Ambassadeur.objects.filter(user=request.user).exists():
        return redirect('dashboard')
    
    # Récupérer l'email de l'utilisateur (utile pour les utilisateurs Google)
    user_email = request.user.email
    
    if request.method == 'POST':
        type_ambassadeur = request.POST.get('type_ambassadeur')
        code_ambassadeur_vie = request.POST.get('code_ambassadeur_vie')
        code_ambassadeur_non_vie = request.POST.get('code_ambassadeur_non_vie')
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        date_naissance = request.POST.get('date_naissance')
        telephone = request.POST.get('telephone')
        email = request.POST.get('email', user_email)
        
        # Vérifications de base
        if not type_ambassadeur or (type_ambassadeur == 'vie' and not code_ambassadeur_vie) or (type_ambassadeur == 'non_vie' and not code_ambassadeur_non_vie) or (type_ambassadeur == 'les_deux' and (not code_ambassadeur_vie or not code_ambassadeur_non_vie)) or not nom or not prenom:
            messages.error(request, "Veuillez remplir tous les champs obligatoires.")
            return render(request, 'authentication/association_code.html', {'type_ambassadeur': type_ambassadeur})
        
        # Recherche d'ambassadeurs existants ayant ces codes
        ambassadeur_existant = None
        
        if code_ambassadeur_vie:
            try:
                ambassadeur_existant = Ambassadeur.objects.get(code_ambassadeur_vie=code_ambassadeur_vie, user__isnull=True)
            except Ambassadeur.DoesNotExist:
                pass
        
        if not ambassadeur_existant and code_ambassadeur_non_vie:
            try:
                ambassadeur_existant = Ambassadeur.objects.get(code_ambassadeur_non_vie=code_ambassadeur_non_vie, user__isnull=True)
            except Ambassadeur.DoesNotExist:
                pass
        
        # Si un ambassadeur avec ce code existe sans utilisateur, l'associer
        if ambassadeur_existant:
            ambassadeur_existant.user = request.user
            
            # Mettre à jour les détails de l'ambassadeur si nécessaire
            if nom and prenom:
                ambassadeur_existant.nom_complet = f"{prenom} {nom}"
            
            if email:
                ambassadeur_existant.email = email
            
            if telephone:
                ambassadeur_existant.telephone = telephone
            
            if date_naissance:
                ambassadeur_existant.date_naissance = date_naissance
            
            # Mettre à jour le type si nécessaire
            if type_ambassadeur and type_ambassadeur != ambassadeur_existant.type_ambassadeur:
                ambassadeur_existant.type_ambassadeur = type_ambassadeur
                
                # Mettre à jour les codes si nécessaire
                if type_ambassadeur == 'vie' or type_ambassadeur == 'les_deux':
                    ambassadeur_existant.code_ambassadeur_vie = code_ambassadeur_vie
                
                if type_ambassadeur == 'non_vie' or type_ambassadeur == 'les_deux':
                    ambassadeur_existant.code_ambassadeur_non_vie = code_ambassadeur_non_vie
            
            ambassadeur_existant.save()
            messages.success(request, "Votre compte a été associé avec succès. Bienvenue dans le programme Ambassadeurs!")
            return redirect('dashboard')
        
        # Sinon, vérifier que les codes n'existent pas déjà chez un autre utilisateur
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
    
    # Vérifier si l'utilisateur s'est connecté via Google
    is_google_user = UserSocialAuth.objects.filter(user=request.user, provider='google-oauth2').exists()
    
    # Préremplir certains champs si l'utilisateur s'est connecté via Google
    context = {
        'is_google_user': is_google_user,
        'user_email': user_email,
        'user_prenom': request.user.first_name,
        'user_nom': request.user.last_name,
    }
    
    return render(request, 'authentication/association_code.html', context)

def logout_view(request):
    """
    Vue pour la déconnexion
    """
    logout(request)
    messages.success(request, "Vous avez été déconnecté avec succès.")
    return redirect('home')