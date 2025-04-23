# backoffice/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.core.paginator import Paginator
import pandas as pd
from django.db.models import Q

import io
from datetime import datetime, timedelta

from ambassadeurs.models import Ambassadeur, Police, Points, Exercice, Configuration
from rewards.models import Recompense, Echange, CategorieRecompense
from authentication.models import UserProfile
from .models import ImportLog, Notification, SystemeConfiguration
from .forms import ImportForm, ExerciceForm, ConfigurationForm, RecompenseForm

# Fonction d'autorisation pour le backoffice
def is_admin(user):
    """Vérifie si l'utilisateur est un administrateur"""
    return user.is_staff or (hasattr(user, 'profile') and user.profile.is_admin)

@login_required
@user_passes_test(is_admin)
def dashboard(request):
    """
    Vue pour le tableau de bord principal du backoffice
    """
    # Statistiques générales
    nb_ambassadeurs = Ambassadeur.objects.filter(actif=True).count()
    nb_polices = Police.objects.filter(statut='payé').count()
    nb_echanges = Echange.objects.count()
    
    # Trouver l'exercice actif
    exercice_actif = Exercice.objects.filter(
        date_debut__lte=timezone.now().date(),
        date_fin__gte=timezone.now().date(),
        actif=True
    ).first()
    
    if not exercice_actif:
        exercice_actif = Exercice.objects.filter(actif=True).order_by('-date_debut').first()
    
    # Statistiques pour l'exercice actif
    if exercice_actif:
        points_distribues = Points.objects.filter(exercice=exercice_actif).aggregate(Sum('montant'))['montant__sum'] or 0
        points_utilises = Echange.objects.filter(exercice=exercice_actif).exclude(statut='annule').aggregate(Sum('points_utilises'))['points_utilises__sum'] or 0
    else:
        points_distribues = 0
        points_utilises = 0
    
    # Derniers échanges à valider
    echanges_en_attente = Echange.objects.filter(statut='en_attente').order_by('-date_creation')[:10]
    
    # Dernières notifications
    notifications = Notification.objects.filter(
        pour_tous=True, 
        date_expiration__gte=timezone.now().date()
    ).order_by('-date_creation')[:5]
    
    context = {
        'nb_ambassadeurs': nb_ambassadeurs,
        'nb_polices': nb_polices,
        'nb_echanges': nb_echanges,
        'exercice_actif': exercice_actif,
        'points_distribues': points_distribues,
        'points_utilises': points_utilises,
        'echanges_en_attente': echanges_en_attente,
        'notifications': notifications,
    }
    
    return render(request, 'backoffice/dashboard.html', context)

@login_required
@user_passes_test(is_admin)
def gestion_ambassadeurs(request):
    """
    Vue pour la gestion des ambassadeurs
    """
    ambassadeurs = Ambassadeur.objects.all().order_by('nom_complet')  # Changé pour utiliser nom_complet au lieu de code_ambassadeur

    
    # Filtrer par statut si spécifié
    statut = request.GET.get('statut')
    if statut == 'actif':
        ambassadeurs = ambassadeurs.filter(actif=True)
    elif statut == 'inactif':
        ambassadeurs = ambassadeurs.filter(actif=False)
    
    # Recherche par nom ou code
    recherche = request.GET.get('recherche')
    if recherche:
        ambassadeurs = ambassadeurs.filter(
            Q(code_ambassadeur_vie__icontains=recherche) |  # Modifié pour utiliser code_ambassadeur_vie
            Q(code_ambassadeur_non_vie__icontains=recherche) |  # Ajouté pour utiliser code_ambassadeur_non_vie
            Q(nom_complet__icontains=recherche)
        )
    
    # Pagination
    paginator = Paginator(ambassadeurs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'statut': statut,
        'recherche': recherche,
    }
    
    return render(request, 'backoffice/gestion_ambassadeurs.html', context)

@login_required
@user_passes_test(is_admin)
def importer_donnees(request):
    """
    Vue pour importer des données depuis les fichiers
    """
    if request.method == 'POST':
        form = ImportForm(request.POST, request.FILES)
        if form.is_valid():
            source = form.cleaned_data['source']
            fichier = request.FILES['fichier']
            
            # Créer un log d'import
            import_log = ImportLog.objects.create(
                source=source,
                fichier=fichier,
                utilisateur=request.user,
                reussi=False
            )
            
            try:
                # Traiter le fichier selon la source
                if source == 'ORASS' or source == 'HELIOS':
                    traiter_import_polices(fichier, source, import_log)
                elif source == 'RH':
                    traiter_import_ambassadeurs(fichier, import_log)
                
                # Marquer l'import comme réussi
                import_log.reussi = True
                import_log.save()
                
                messages.success(request, f"Import des données {source} réussi.")
                return redirect('backoffice:import_logs')
            
            except Exception as e:
                import_log.message_erreur = str(e)
                import_log.save()
                messages.error(request, f"Erreur lors de l'import : {str(e)}")
    else:
        form = ImportForm()
    
    return render(request, 'backoffice/importer_donnees.html', {'form': form})

@login_required
@user_passes_test(is_admin)
def gestion_recompenses(request):
    """
    Vue pour la gestion des récompenses
    """
    recompenses = Recompense.objects.all().order_by('categorie__ordre', 'cout_points')
    
    # Filtrer par catégorie si spécifié
    categorie_id = request.GET.get('categorie')
    if categorie_id:
        recompenses = recompenses.filter(categorie_id=categorie_id)
    
    # Filtrer par statut
    statut = request.GET.get('statut')
    if statut == 'actif':
        recompenses = recompenses.filter(actif=True)
    elif statut == 'inactif':
        recompenses = recompenses.filter(actif=False)
    
    # Pagination
    paginator = Paginator(recompenses, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    # Liste des catégories pour le filtre
    categories = CategorieRecompense.objects.all().order_by('ordre')
    
    context = {
        'page_obj': page_obj,
        'categories': categories,
        'categorie_id': categorie_id,
        'statut': statut,
    }
    
    return render(request, 'backoffice/gestion_recompenses.html', context)

@login_required
@user_passes_test(is_admin)
def gestion_echanges(request):
    """
    Vue pour la gestion des échanges
    """
    echanges = Echange.objects.all().order_by('-date_creation')
    
    # Filtrer par statut
    statut = request.GET.get('statut')
    if statut and statut != 'tous':
        echanges = echanges.filter(statut=statut)
    
    # Filtrer par ambassadeur
    ambassadeur_id = request.GET.get('ambassadeur')
    if ambassadeur_id:
        echanges = echanges.filter(ambassadeur_id=ambassadeur_id)
    
    # Filtrer par date
    date_debut = request.GET.get('date_debut')
    if date_debut:
        echanges = echanges.filter(date_creation__gte=date_debut)
    
    date_fin = request.GET.get('date_fin')
    if date_fin:
        echanges = echanges.filter(date_creation__lte=date_fin)
    
    # Pagination
    paginator = Paginator(echanges, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'statuts': Echange.STATUS_CHOICES,
        'statut_selectionne': statut,
        'ambassadeur_id': ambassadeur_id,
        'date_debut': date_debut,
        'date_fin': date_fin,
    }
    
    return render(request, 'backoffice/gestion_echanges.html', context)

@login_required
@user_passes_test(is_admin)
def valider_echange(request, echange_id):
    """
    Vue pour valider un échange
    """
    echange = get_object_or_404(Echange, pk=echange_id)
    
    if request.method == 'POST':
        nouveau_statut = request.POST.get('statut')
        commentaire = request.POST.get('commentaire', '')
        
        # Mettre à jour le statut de l'échange
        echange.statut = nouveau_statut
        if commentaire:
            echange.commentaire = commentaire
        echange.save()
        
        messages.success(request, f"Échange #{echange_id} mis à jour avec succès.")
        return redirect('backoffice:gestion_echanges')
    
    context = {
        'echange': echange,
        'statuts': Echange.STATUS_CHOICES,
    }
    
    return render(request, 'backoffice/valider_echange.html', context)

@login_required
@user_passes_test(is_admin)
def configuration_systeme(request):
    """
    Vue pour la configuration du système
    """
    # Récupérer la configuration du programme
    config, created = Configuration.objects.get_or_create(pk=1)
    
    if request.method == 'POST':
        form = ConfigurationForm(request.POST, instance=config)
        if form.is_valid():
            form.save()
            messages.success(request, "Configuration mise à jour avec succès.")
            return redirect('backoffice:configuration_systeme')
    else:
        form = ConfigurationForm(instance=config)
    
    # Récupérer les exercices
    exercices = Exercice.objects.all().order_by('-date_debut')
    
    context = {
        'form': form,
        'exercices': exercices,
    }
    
    return render(request, 'backoffice/configuration_systeme.html', context)

@login_required
@user_passes_test(is_admin)
def gestion_exercices(request):
    """
    Vue pour la gestion des exercices
    """
    if request.method == 'POST':
        form = ExerciceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Exercice créé avec succès.")
            return redirect('backoffice:gestion_exercices')
    else:
        form = ExerciceForm()
    
    exercices = Exercice.objects.all().order_by('-date_debut')
    
    context = {
        'form': form,
        'exercices': exercices,
    }
    
    return render(request, 'backoffice/gestion_exercices.html', context)

@login_required
@user_passes_test(is_admin)
def rapport_points(request):
    """
    Vue pour générer des rapports sur les points
    """
    # Récupérer l'exercice sélectionné
    exercice_id = request.GET.get('exercice')
    if exercice_id:
        exercice = get_object_or_404(Exercice, pk=exercice_id)
    else:
        # Prendre l'exercice actif par défaut
        exercice = Exercice.objects.filter(
            date_debut__lte=timezone.now().date(),
            date_fin__gte=timezone.now().date(),
            actif=True
        ).first() or Exercice.objects.filter(actif=True).order_by('-date_debut').first()
    
    # Liste des exercices pour le filtre
    exercices = Exercice.objects.all().order_by('-date_debut')
    
    # Générer le rapport
    if exercice:
        # Points distribués par ambassadeur
        points_par_ambassadeur = Points.objects.filter(exercice=exercice).values(
            'ambassadeur__code_ambassadeur', 'ambassadeur__nom_complet'
        ).annotate(
            total_points=Sum('montant')
        ).order_by('-total_points')
        
        # Points utilisés par ambassadeur
        points_utilises = Echange.objects.filter(exercice=exercice).exclude(
            statut='annule'
        ).values(
            'ambassadeur__code_ambassadeur', 'ambassadeur__nom_complet'
        ).annotate(
            total_utilises=Sum('points_utilises')
        ).order_by('-total_utilises')
        
        # Exporter en CSV si demandé
        if request.GET.get('export') == 'csv':
            return exporter_rapport_points_csv(points_par_ambassadeur, points_utilises, exercice)
    else:
        points_par_ambassadeur = []
        points_utilises = []
    
    context = {
        'exercice': exercice,
        'exercices': exercices,
        'points_par_ambassadeur': points_par_ambassadeur,
        'points_utilises': points_utilises,
    }
    
    return render(request, 'backoffice/rapport_points.html', context)

# Fonctions utilitaires pour le backoffice

def traiter_import_polices(fichier, source, import_log):
    """
    Traite l'import d'un fichier de polices
    """
    # Lire le fichier CSV
    df = pd.read_csv(
        io.StringIO(fichier.read().decode('utf-8')),
        delimiter=';',  # Adapté selon le format du fichier
        dtype={'numero_police': str, 'code_ambassadeur': str}
    )
    
    # Vérifier les colonnes requises
    colonnes_requises = ['numero_police', 'code_ambassadeur', 'prime_nette', 'date_paiement']
    for col in colonnes_requises:
        if col not in df.columns:
            raise ValueError(f"Colonne requise manquante dans le fichier : {col}")
    
    # Convertir les colonnes de date
    df['date_paiement'] = pd.to_datetime(df['date_paiement'], format='%d/%m/%Y')
    
    # Compter les lignes
    import_log.nombre_enregistrements = len(df)
    import_log.save()
    
    # Importer chaque ligne
    for _, row in df.iterrows():
        try:
            # Vérifier si la police existe déjà
            if Police.objects.filter(numero_police=row['numero_police']).exists():
                continue
            
            # Vérifier si l'ambassadeur existe
            try:
                ambassadeur = Ambassadeur.objects.get(code_ambassadeur=row['code_ambassadeur'])
            except Ambassadeur.DoesNotExist:
                # Ignorer cette police
                continue
            
            # Créer la police
            Police.objects.create(
                numero_police=row['numero_police'],
                ambassadeur=ambassadeur,
                prime_nette=row['prime_nette'],
                statut='payé',
                source_systeme=source,
                date_paiement=row['date_paiement']
            )
        except Exception as e:
            # Continuer malgré les erreurs
            continue

def traiter_import_ambassadeurs(fichier, import_log):
    """
    Traite l'import d'un fichier d'ambassadeurs
    """
    # Lire le fichier CSV
    df = pd.read_csv(
        io.StringIO(fichier.read().decode('utf-8')),
        delimiter=';',  # Adapté selon le format du fichier
        dtype={'code_ambassadeur': str}
    )
    
    # Vérifier les colonnes requises
    colonnes_requises = ['code_ambassadeur', 'nom_complet', 'email', 'identifiant_ad']
    for col in colonnes_requises:
        if col not in df.columns:
            raise ValueError(f"Colonne requise manquante dans le fichier : {col}")
    
    # Compter les lignes
    import_log.nombre_enregistrements = len(df)
    import_log.save()
    
    # Importer chaque ligne
    for _, row in df.iterrows():
        try:
            # Vérifier si l'utilisateur existe
            from django.contrib.auth.models import User
            
            user, created = User.objects.get_or_create(
                username=row['identifiant_ad'],
                defaults={
                    'email': row['email'],
                    'is_active': True
                }
            )
            
            # Mettre à jour ou créer l'ambassadeur
            ambassadeur, created = Ambassadeur.objects.get_or_create(
                code_ambassadeur=row['code_ambassadeur'],
                defaults={
                    'user': user,
                    'nom_complet': row['nom_complet'],
                    'email': row['email'],
                    'actif': True
                }
            )
            
            if not created:
                # Mettre à jour les informations
                ambassadeur.nom_complet = row['nom_complet']
                ambassadeur.email = row['email']
                ambassadeur.save()
        except Exception as e:
            # Continuer malgré les erreurs
            continue

def exporter_rapport_points_csv(points_par_ambassadeur, points_utilises, exercice):
    """
    Exporte le rapport de points au format CSV
    """
    # Préparer les données
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="rapport_points_{exercice.nom}.csv"'
    
    # Créer le writer CSV
    import csv
    writer = csv.writer(response, delimiter=';')
    
    # Écrire l'en-tête
    writer.writerow(['Code Ambassadeur', 'Nom Complet', 'Points Gagnés', 'Points Utilisés', 'Solde'])
    
    # Convertir les données en dictionnaires pour fusionner les résultats
    dict_points = {row['ambassadeur__nom_complet']: { 
        'code': row['ambassadeur__nom_complet'],
        'nom': row['ambassadeur__nom_complet'],
        'gagnes': row['total_points'],
        'utilises': 0,
        'solde': row['total_points']
    } for row in points_par_ambassadeur}
    
    # Ajouter les points utilisés
    for row in points_utilises:
        code = row['ambassadeur__code_ambassadeur']
        if code in dict_points:
            dict_points[code]['utilises'] = row['total_utilises']
            dict_points[code]['solde'] -= row['total_utilises']
        else:
            dict_points[code] = {
                'code': code,
                'nom': row['ambassadeur__nom_complet'],
                'gagnes': 0,
                'utilises': row['total_utilises'],
                'solde': -row['total_utilises']
            }
    
    # Écrire les données
    for code, data in dict_points.items():
        writer.writerow([data['code'], data['nom'], data['gagnes'], data['utilises'], data['solde']])
    
    return response

@login_required
@user_passes_test(is_admin)
def gestion_codes_ambassadeurs(request):
    """
    Vue pour la gestion des codes ambassadeurs
    """
    # Récupérer tous les ambassadeurs
    ambassadeurs = Ambassadeur.objects.all().order_by('nom_complet')
    
    # Filtrage
    type_filtre = request.GET.get('type', 'tous')
    statut = request.GET.get('statut')
    recherche = request.GET.get('recherche')
    
    if type_filtre != 'tous':
        if type_filtre == 'vie':
            ambassadeurs = ambassadeurs.filter(type_ambassadeur__in=['vie', 'les_deux'])
        elif type_filtre == 'non_vie':
            ambassadeurs = ambassadeurs.filter(type_ambassadeur__in=['non_vie', 'les_deux'])
    
    if statut == 'associe':
        ambassadeurs = ambassadeurs.filter(user__isnull=False)
    elif statut == 'non_associe':
        ambassadeurs = ambassadeurs.filter(user__isnull=True)
    
    if recherche:
        ambassadeurs = ambassadeurs.filter(
            Q(code_ambassadeur_vie__icontains=recherche) |
            Q(code_ambassadeur_non_vie__icontains=recherche) |
            Q(nom_complet__icontains=recherche) |
            Q(email__icontains=recherche)
        )
    
    # Pagination
    paginator = Paginator(ambassadeurs, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'type_filtre': type_filtre,
        'statut': statut,
        'recherche': recherche,
    }
    
    return render(request, 'backoffice/gestion_codes_ambassadeurs.html', context)

@login_required
@user_passes_test(is_admin)
def ajouter_code_ambassadeur(request):
    """
    Vue pour ajouter un code ambassadeur
    """
    if request.method == 'POST':
        type_ambassadeur = request.POST.get('type_ambassadeur')
        code_vie = request.POST.get('code_ambassadeur_vie')
        code_non_vie = request.POST.get('code_ambassadeur_non_vie')
        nom_complet = request.POST.get('nom_complet', '')
        email = request.POST.get('email', '')
        
        if not type_ambassadeur or (type_ambassadeur == 'vie' and not code_vie) or (type_ambassadeur == 'non_vie' and not code_non_vie) or (type_ambassadeur == 'les_deux' and (not code_vie or not code_non_vie)):
            messages.error(request, "Veuillez remplir tous les champs obligatoires.")
        else:
            # Vérifier que les codes n'existent pas déjà
            if code_vie and Ambassadeur.objects.filter(code_ambassadeur_vie=code_vie).exists():
                messages.error(request, "Ce code ambassadeur Vie existe déjà.")
            elif code_non_vie and Ambassadeur.objects.filter(code_ambassadeur_non_vie=code_non_vie).exists():
                messages.error(request, "Ce code ambassadeur Non-Vie existe déjà.")
            else:
                # Créer un nouvel ambassadeur sans utilisateur associé
                Ambassadeur.objects.create(
                    type_ambassadeur=type_ambassadeur,
                    code_ambassadeur_vie=code_vie if type_ambassadeur in ['vie', 'les_deux'] else None,
                    code_ambassadeur_non_vie=code_non_vie if type_ambassadeur in ['non_vie', 'les_deux'] else None,
                    nom_complet=nom_complet,
                    email=email,
                    actif=True
                )
                messages.success(request, "Le code ambassadeur a été créé avec succès.")
                return redirect('backoffice:gestion_codes_ambassadeurs')
    
    return render(request, 'backoffice/ajouter_code_ambassadeur.html')

@login_required
@user_passes_test(is_admin)
def dissocier_ambassadeur(request, ambassadeur_id):
    """
    Vue pour dissocier un ambassadeur de son utilisateur
    """
    if request.method == 'POST':
        ambassadeur = get_object_or_404(Ambassadeur, pk=ambassadeur_id)
        
        if ambassadeur.user:
            # Sauvegarder l'ancien utilisateur pour le message
            ancien_user = ambassadeur.user.username
            
            # Dissocier l'utilisateur
            ambassadeur.user = None
            ambassadeur.save()
            
            messages.success(request, f"L'ambassadeur {ambassadeur.nom_complet} a été dissocié de l'utilisateur {ancien_user}.")
        else:
            messages.warning(request, "Cet ambassadeur n'était associé à aucun utilisateur.")
        
        return redirect('backoffice:gestion_codes_ambassadeurs')
    
    # Si ce n'est pas une requête POST, rediriger vers la liste
    return redirect('backoffice:gestion_codes_ambassadeurs')

@login_required
@user_passes_test(is_admin)
def modifier_ambassadeur(request, ambassadeur_id):
    """
    Vue pour modifier un ambassadeur
    """
    ambassadeur = get_object_or_404(Ambassadeur, pk=ambassadeur_id)
    
    if request.method == 'POST':
        type_ambassadeur = request.POST.get('type_ambassadeur')
        code_vie = request.POST.get('code_ambassadeur_vie')
        code_non_vie = request.POST.get('code_ambassadeur_non_vie')
        nom_complet = request.POST.get('nom_complet')
        email = request.POST.get('email')
        telephone = request.POST.get('telephone')
        date_naissance = request.POST.get('date_naissance')
        actif = request.POST.get('actif') == 'on'
        
        # Vérification des codes
        if (type_ambassadeur == 'vie' or type_ambassadeur == 'les_deux') and code_vie:
            code_vie_exists = Ambassadeur.objects.filter(code_ambassadeur_vie=code_vie).exclude(pk=ambassadeur_id).exists()
            if code_vie_exists:
                messages.error(request, "Ce code ambassadeur Vie est déjà utilisé par un autre ambassadeur.")
                return render(request, 'backoffice/modifier_ambassadeur.html', {'ambassadeur': ambassadeur})
        
        if (type_ambassadeur == 'non_vie' or type_ambassadeur == 'les_deux') and code_non_vie:
            code_non_vie_exists = Ambassadeur.objects.filter(code_ambassadeur_non_vie=code_non_vie).exclude(pk=ambassadeur_id).exists()
            if code_non_vie_exists:
                messages.error(request, "Ce code ambassadeur Non-Vie est déjà utilisé par un autre ambassadeur.")
                return render(request, 'backoffice/modifier_ambassadeur.html', {'ambassadeur': ambassadeur})
        
        # Mise à jour de l'ambassadeur
        ambassadeur.type_ambassadeur = type_ambassadeur
        ambassadeur.code_ambassadeur_vie = code_vie if type_ambassadeur in ['vie', 'les_deux'] else None
        ambassadeur.code_ambassadeur_non_vie = code_non_vie if type_ambassadeur in ['non_vie', 'les_deux'] else None
        ambassadeur.nom_complet = nom_complet
        ambassadeur.email = email
        ambassadeur.telephone = telephone
        ambassadeur.date_naissance = date_naissance if date_naissance else None
        ambassadeur.actif = actif
        ambassadeur.save()
        
        messages.success(request, f"L'ambassadeur {ambassadeur.nom_complet} a été mis à jour avec succès.")
        return redirect('backoffice:gestion_codes_ambassadeurs')
    
    return render(request, 'backoffice/modifier_ambassadeur.html', {'ambassadeur': ambassadeur})

@login_required
@user_passes_test(is_admin)
def detail_ambassadeur(request, ambassadeur_id):
    """
    Vue pour afficher les détails d'un ambassadeur
    """
    ambassadeur = get_object_or_404(Ambassadeur, pk=ambassadeur_id)
    
    # Récupérer l'exercice actif
    exercice_actif = Exercice.objects.filter(
        date_debut__lte=timezone.now().date(),
        date_fin__gte=timezone.now().date(),
        actif=True
    ).first() or Exercice.objects.filter(actif=True).order_by('-date_debut').first()
    
    # Statistiques
    points_vie = Points.objects.filter(ambassadeur=ambassadeur, type_assurance='vie').aggregate(Sum('montant'))['montant__sum'] or 0
    points_non_vie = Points.objects.filter(ambassadeur=ambassadeur, type_assurance='non_vie').aggregate(Sum('montant'))['montant__sum'] or 0
    
    polices_vie = Police.objects.filter(ambassadeur=ambassadeur, type_assurance='vie').count()
    polices_non_vie = Police.objects.filter(ambassadeur=ambassadeur, type_assurance='non_vie').count()
    
    # Dernières transactions
    polices = Police.objects.filter(ambassadeur=ambassadeur).order_by('-date_paiement')[:5]
    points = Points.objects.filter(ambassadeur=ambassadeur).order_by('-date_creation')[:5]
    echanges = Echange.objects.filter(ambassadeur=ambassadeur).order_by('-date_creation')[:5]
    
    context = {
        'ambassadeur': ambassadeur,
        'exercice_actif': exercice_actif,
        'points_vie': points_vie,
        'points_non_vie': points_non_vie,
        'polices_vie': polices_vie,
        'polices_non_vie': polices_non_vie,
        'polices': polices,
        'points': points,
        'echanges': echanges,
    }
    
    return render(request, 'backoffice/detail_ambassadeur.html', context)