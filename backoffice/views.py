# backoffice/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.db.models import Sum, Count
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.core.paginator import Paginator
import pandas as pd
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
    ambassadeurs = Ambassadeur.objects.all().order_by('code_ambassadeur')
    
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
            code_ambassadeur__icontains=recherche
        ) | ambassadeurs.filter(
            nom_complet__icontains=recherche
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
    dict_points = {row['ambassadeur__code_ambassadeur']: {
        'code': row['ambassadeur__code_ambassadeur'],
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
    # Récupérer tous les codes ambassadeurs
    codes = Ambassadeur.objects.all().order_by('code_ambassadeur')
    
    # Filtrage
    statut = request.GET.get('statut')
    recherche = request.GET.get('recherche')
    
    if statut == 'associe':
        codes = codes.filter(user__isnull=False)
    elif statut == 'non_associe':
        codes = codes.filter(user__isnull=True)
    
    if recherche:
        codes = codes.filter(
            code_ambassadeur__icontains=recherche
        ) | codes.filter(
            nom_complet__icontains=recherche
        )
    
    # Pagination
    paginator = Paginator(codes, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
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
        code = request.POST.get('code_ambassadeur')
        nom = request.POST.get('nom_complet', '')
        
        if code:
            # Vérifier si le code existe déjà
            if Ambassadeur.objects.filter(code_ambassadeur=code).exists():
                messages.error(request, "Ce code ambassadeur existe déjà.")
            else:
                # Créer un nouvel ambassadeur sans utilisateur associé
                Ambassadeur.objects.create(
                    code_ambassadeur=code,
                    nom_complet=nom,
                    actif=True
                )
                messages.success(request, f"Le code ambassadeur {code} a été créé avec succès.")
                return redirect('backoffice:gestion_codes_ambassadeurs')
        else:
            messages.error(request, "Le code ambassadeur est obligatoire.")
    
    return render(request, 'backoffice/ajouter_code_ambassadeur.html')

@login_required
@user_passes_test(is_admin)
def dissocier_code_ambassadeur(request, ambassadeur_id):
    """
    Vue pour dissocier un code ambassadeur de son utilisateur
    """
    if request.method == 'POST':
        ambassadeur = get_object_or_404(Ambassadeur, pk=ambassadeur_id)
        
        if ambassadeur.user:
            # Sauvegarder l'ancien code pour le message
            ancien_code = ambassadeur.code_ambassadeur
            ancien_user = ambassadeur.user.username
            
            # Dissocier l'utilisateur
            ambassadeur.user = None
            ambassadeur.save()
            
            messages.success(request, f"Le code {ancien_code} a été dissocié de l'utilisateur {ancien_user}.")
        else:
            messages.warning(request, "Ce code n'était associé à aucun utilisateur.")
        
        return redirect('backoffice:gestion_codes_ambassadeurs')
    
    # Si ce n'est pas une requête POST, rediriger vers la liste
    return redirect('backoffice:gestion_codes_ambassadeurs')