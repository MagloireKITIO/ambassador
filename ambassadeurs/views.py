# ambassadeurs/views.py

import csv
from datetime import timedelta
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Sum, Count
from django.utils import timezone
from django.db.models.functions import TruncMonth
from django.core.paginator import Paginator


from .models import Ambassadeur, Police, Points, Exercice
from rewards.models import Recompense, Echange


@login_required
def dashboard(request):
    """
    Vue du tableau de bord principal pour les ambassadeurs
    """
    try:
        # Récupérer l'ambassadeur associé à l'utilisateur
        ambassadeur = Ambassadeur.objects.get(user=request.user)
        
        # Récupérer l'exercice actif
        exercice_actif = Exercice.objects.filter(
            date_debut__lte=timezone.now().date(),
            date_fin__gte=timezone.now().date(),
            actif=True
        ).first()
        
        if not exercice_actif:
            # Si aucun exercice actif, prendre le plus récent
            exercice_actif = Exercice.objects.filter(actif=True).order_by('-date_debut').first()
        
        # Récupérer tous les exercices pour sélection
        exercices = Exercice.objects.filter(actif=True).order_by('-date_debut')
        
        # Calculer les points disponibles pour l'exercice actif
        points_exercice = ambassadeur.get_solde_points(exercice_actif)
        
        # Calculer les points totaux
        points_total = ambassadeur.get_solde_points()
        
        # Récupérer les dernières polices
        derniers_polices = Police.objects.filter(
            ambassadeur=ambassadeur,
            statut='payé'
        ).order_by('-date_paiement')[:5]
        
        # Récupérer les derniers échanges
        derniers_echanges = Echange.objects.filter(
            ambassadeur=ambassadeur
        ).order_by('-date_creation')[:5]
        
        # Récupérer quelques récompenses recommandées
        recompenses_recommandees = Recompense.objects.filter(
            actif=True,
            cout_points__lte=points_exercice
        ).order_by('cout_points')[:4]
        
        context = {
            'ambassadeur': ambassadeur,
            'exercice_actif': exercice_actif,
            'exercices': exercices,
            'points_exercice': points_exercice,
            'points_total': points_total,
            'derniers_polices': derniers_polices,
            'derniers_echanges': derniers_echanges,
            'recompenses_recommandees': recompenses_recommandees,
        }
        
        return render(request, 'ambassadeurs/dashboard.html', context)
    
    except Ambassadeur.DoesNotExist:
        messages.error(request, "Vous n'êtes pas enregistré comme ambassadeur.")
        return redirect('login')

@login_required
def historique_points(request):
    """
    Vue pour afficher l'historique des points avec graphique et filtres avancés
    """
    try:
        ambassadeur = Ambassadeur.objects.get(user=request.user)
        
        # Filtrer par exercice si spécifié
        exercice_id = request.GET.get('exercice')
        if exercice_id:
            exercice = get_object_or_404(Exercice, pk=exercice_id, actif=True)
            points = Points.objects.filter(ambassadeur=ambassadeur, exercice=exercice)
        else:
            # Par défaut, prendre l'exercice actif
            exercice = Exercice.objects.filter(
                date_debut__lte=timezone.now().date(),
                date_fin__gte=timezone.now().date(),
                actif=True
            ).first()
            
            if exercice:
                points = Points.objects.filter(ambassadeur=ambassadeur, exercice=exercice)
            else:
                points = Points.objects.filter(ambassadeur=ambassadeur)
        
        # Trier par date de création (décroissant)
        points = points.order_by('-date_creation')
        
        # Récupérer tous les exercices pour le filtre
        exercices = Exercice.objects.filter(actif=True).order_by('-date_debut')
        
        # Calculer les statistiques
        points_gagnes = points.aggregate(Sum('montant'))['montant__sum'] or 0
        points_utilises = Echange.objects.filter(
            ambassadeur=ambassadeur,
            exercice=exercice if exercice_id else None
        ).exclude(statut='annule').aggregate(Sum('points_utilises'))['points_utilises__sum'] or 0
        
        points_disponibles = points_gagnes - points_utilises
        
        # Calculer les points qui vont expirer dans les 30 jours
        date_30j = timezone.now().date() + timedelta(days=30)
        points_expirants = points.filter(
            date_expiration__lte=date_30j,
            date_expiration__gte=timezone.now().date()
        ).aggregate(Sum('montant'))['montant__sum'] or 0
        
        # Regrouper les points par mois
        points_par_mois_query = Points.objects.filter(
            ambassadeur=ambassadeur,
            exercice=exercice if exercice_id else None
        ).annotate(
            month=TruncMonth('date_creation')
        ).values('month').annotate(
            total=Sum('montant')
        ).order_by('month')
        
        # Formatter les données pour le graphique
        points_par_mois = []
        for item in points_par_mois_query:
            points_par_mois.append({
                'month': item['month'].strftime('%b %Y'),
                'total': item['total']
            })
        
        context = {
            'ambassadeur': ambassadeur,
            'points': points,
            'exercices': exercices,
            'exercice_selectionne': exercice,
            'points_gagnes': points_gagnes,
            'points_disponibles': points_disponibles,
            'points_expirants': points_expirants,
            'points_par_mois': points_par_mois,
            'now': timezone.now().date(),
        }
        
        return render(request, 'ambassadeurs/historique_points.html', context)
    
    except Ambassadeur.DoesNotExist:
        messages.error(request, "Vous n'êtes pas enregistré comme ambassadeur.")
        return redirect('login')
    
@login_required
def exporter_historique_points(request):
    """
    Exporte l'historique des points au format CSV
    """
    try:
        ambassadeur = Ambassadeur.objects.get(user=request.user)
        
        # Filtrer par exercice si spécifié
        exercice_id = request.GET.get('exercice')
        if exercice_id:
            exercice = get_object_or_404(Exercice, pk=exercice_id, actif=True)
            points = Points.objects.filter(ambassadeur=ambassadeur, exercice=exercice)
            filename = f"historique_points_{exercice.nom}.csv"
        else:
            points = Points.objects.filter(ambassadeur=ambassadeur)
            filename = "historique_points_complet.csv"
        
        # Trier par date de création (décroissant)
        points = points.order_by('-date_creation')
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        writer = csv.writer(response)
        writer.writerow(['Date', 'Police', 'Description', 'Montant', 'Date d\'expiration'])
        
        for point in points:
            writer.writerow([
                point.date_creation.strftime('%d/%m/%Y'),
                point.police.numero_police if point.police else '-',
                point.description,
                point.montant,
                point.date_expiration.strftime('%d/%m/%Y') if point.date_expiration else '-'
            ])
        
        return response
    
    except Ambassadeur.DoesNotExist:
        messages.error(request, "Vous n'êtes pas enregistré comme ambassadeur.")
        return redirect('login')
    
@login_required
def historique_polices(request):
    """
    Vue pour afficher l'historique des polices avec graphiques et filtres avancés
    """
    try:
        ambassadeur = Ambassadeur.objects.get(user=request.user)
        
        # Filtrer par date si spécifié
        date_debut = request.GET.get('date_debut')
        date_fin = request.GET.get('date_fin')
        source = request.GET.get('source')
        
        polices = Police.objects.filter(ambassadeur=ambassadeur)
        
        if date_debut:
            polices = polices.filter(date_paiement__gte=date_debut)
        
        if date_fin:
            polices = polices.filter(date_paiement__lte=date_fin)
        
        if source:
            polices = polices.filter(source_systeme=source)
        
        # Trier par date de paiement (décroissant)
        polices = polices.order_by('-date_paiement')
        
        # Calculer les statistiques
        total_polices = polices.count()
        total_primes = polices.aggregate(Sum('prime_nette'))['prime_nette__sum'] or 0
        
        # Calculer le total des points générés
        total_points = 0
        for police in polices:
            points = police.points.aggregate(Sum('montant'))['montant__sum'] or 0
            total_points += points
        
        # Regrouper les polices par mois
        polices_par_mois_query = Police.objects.filter(
            ambassadeur=ambassadeur
        )
        
        if date_debut:
            polices_par_mois_query = polices_par_mois_query.filter(date_paiement__gte=date_debut)
        
        if date_fin:
            polices_par_mois_query = polices_par_mois_query.filter(date_paiement__lte=date_fin)
        
        polices_par_mois_query = polices_par_mois_query.annotate(
            month=TruncMonth('date_paiement')
        ).values('month').annotate(
            count=Count('id'),
            amount=Sum('prime_nette')
        ).order_by('month')
        
        # Formatter les données pour le graphique
        polices_par_mois = []
        for item in polices_par_mois_query:
            polices_par_mois.append({
                'month': item['month'].strftime('%b %Y'),
                'count': item['count'],
                'amount': item['amount']
            })
        
        # Compter les polices par source
        sources_count = {}
        for source_systeme in ['ORASS', 'HELIOS']:
            count = polices.filter(source_systeme=source_systeme).count()
            if count > 0:
                sources_count[source_systeme] = count
        
        # Pagination
        paginator = Paginator(polices, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'ambassadeur': ambassadeur,
            'polices': page_obj,
            'date_debut': date_debut,
            'date_fin': date_fin,
            'source': source,
            'total_polices': total_polices,
            'total_primes': total_primes,
            'total_points': total_points,
            'polices_par_mois': polices_par_mois,
            'sources_count': sources_count
        }
        
        return render(request, 'ambassadeurs/historique_polices.html', context)
    
    except Ambassadeur.DoesNotExist:
        messages.error(request, "Vous n'êtes pas enregistré comme ambassadeur.")
        return redirect('login')

@login_required
def exporter_historique_polices(request):
    """
    Exporte l'historique des polices au format CSV
    """
    try:
        ambassadeur = Ambassadeur.objects.get(user=request.user)
        
        # Filtrer par date si spécifié
        date_debut = request.GET.get('date_debut')
        date_fin = request.GET.get('date_fin')
        source = request.GET.get('source')
        
        polices = Police.objects.filter(ambassadeur=ambassadeur)
        
        if date_debut:
            polices = polices.filter(date_paiement__gte=date_debut)
            filename_parts = [f"depuis_{date_debut}"]
        else:
            filename_parts = []
        
        if date_fin:
            polices = polices.filter(date_paiement__lte=date_fin)
            filename_parts.append(f"jusqua_{date_fin}")
        
        if source:
            polices = polices.filter(source_systeme=source)
            filename_parts.append(source)
        
        # Trier par date de paiement (décroissant)
        polices = polices.order_by('-date_paiement')
        
 
        response = HttpResponse(content_type='text/csv')
        
        if filename_parts:
            filename = f"historique_polices_{'_'.join(filename_parts)}.csv"
        else:
            filename = "historique_polices_complet.csv"
        
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        writer = csv.writer(response)
        writer.writerow(['Numéro police', 'Date paiement', 'Source', 'Prime nette', 'Points générés', 'Statut'])
        
        for police in polices:
            points = police.points.aggregate(Sum('montant'))['montant__sum'] or 0
            writer.writerow([
                police.numero_police,
                police.date_paiement.strftime('%d/%m/%Y'),
                police.source_systeme,
                police.prime_nette,
                points,
                police.statut
            ])
        
        return response
    
    except Ambassadeur.DoesNotExist:
        messages.error(request, "Vous n'êtes pas enregistré comme ambassadeur.")
        return redirect('login')


@login_required
def historique_echanges(request):
    """
    Vue pour afficher l'historique des échanges avec graphiques et filtres avancés
    """
    try:
        ambassadeur = Ambassadeur.objects.get(user=request.user)
        
        # Filtrer par statut
        statut = request.GET.get('statut')
        
        echanges = Echange.objects.filter(ambassadeur=ambassadeur)
        
        if statut and statut != 'tous':
            echanges = echanges.filter(statut=statut)
        
        # Filtrer par période
        periode = request.GET.get('date', 'tous')
        today = timezone.now().date()
        
        if periode == 'recent':
            date_debut = today - timedelta(days=30)
            echanges = echanges.filter(date_creation__gte=date_debut)
        elif periode == 'mois_courant':
            date_debut = today.replace(day=1)
            echanges = echanges.filter(date_creation__gte=date_debut)
        elif periode == 'mois_precedent':
            date_debut = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
            date_fin = today.replace(day=1) - timedelta(days=1)
            echanges = echanges.filter(date_creation__gte=date_debut, date_creation__lte=date_fin)
        elif periode == 'annee':
            date_debut = today.replace(month=1, day=1)
            echanges = echanges.filter(date_creation__gte=date_debut)
        
        # Trier par date de création (décroissant)
        echanges = echanges.order_by('-date_creation')
        
        # Calculer les statistiques
        total_echanges = echanges.count()
        en_attente = echanges.filter(statut='en_attente').count()
        completes = echanges.filter(statut__in=['confirme', 'expedie', 'livre']).count()
        points_utilises = echanges.exclude(statut='annule').aggregate(Sum('points_utilises'))['points_utilises__sum'] or 0
        
        # Compter les échanges par statut
        statuts_count = {}
        for statut_code, statut_label in Echange.STATUS_CHOICES:
            count = echanges.filter(statut=statut_code).count()
            if count > 0:
                statuts_count[statut_label] = count
        
        # Pagination
        paginator = Paginator(echanges, 5)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'ambassadeur': ambassadeur,
            'echanges': page_obj,
            'statuts': Echange.STATUS_CHOICES,
            'statut_selectionne': statut or 'tous',
            'periode': periode,
            'total_echanges': total_echanges,
            'en_attente': en_attente,
            'completes': completes,
            'points_utilises': points_utilises,
            'statuts_count': statuts_count
        }
        
        return render(request, 'ambassadeurs/historique_echanges.html', context)
    
    except Ambassadeur.DoesNotExist:
        messages.error(request, "Vous n'êtes pas enregistré comme ambassadeur.")
        return redirect('login')
    
@login_required
def exporter_historique_echanges(request):
    """
    Exporte l'historique des échanges au format CSV
    """
    try:
        ambassadeur = Ambassadeur.objects.get(user=request.user)
        
        # Filtrer par statut
        statut = request.GET.get('statut')
        
        echanges = Echange.objects.filter(ambassadeur=ambassadeur)
        
        if statut and statut != 'tous':
            echanges = echanges.filter(statut=statut)
            filename_parts = [f"statut_{statut}"]
        else:
            filename_parts = []
        
        # Filtrer par période
        periode = request.GET.get('date', 'tous')
        today = timezone.now().date()
        
        if periode == 'recent':
            date_debut = today - timedelta(days=30)
            echanges = echanges.filter(date_creation__gte=date_debut)
            filename_parts.append('30j')
        elif periode == 'mois_courant':
            date_debut = today.replace(day=1)
            echanges = echanges.filter(date_creation__gte=date_debut)
            filename_parts.append('mois_courant')
        elif periode == 'mois_precedent':
            date_debut = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
            date_fin = today.replace(day=1) - timedelta(days=1)
            echanges = echanges.filter(date_creation__gte=date_debut, date_creation__lte=date_fin)
            filename_parts.append('mois_precedent')
        elif periode == 'annee':
            date_debut = today.replace(month=1, day=1)
            echanges = echanges.filter(date_creation__gte=date_debut)
            filename_parts.append('annee_courante')
        
        # Trier par date de création (décroissant)
        echanges = echanges.order_by('-date_creation')
        
        # Générer le fichier CSV
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        
        if filename_parts:
            filename = f"historique_echanges_{'_'.join(filename_parts)}.csv"
        else:
            filename = "historique_echanges_complet.csv"
        
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        writer = csv.writer(response)
        writer.writerow(['Date', 'Récompense', 'Points utilisés', 'Statut', 'Date de modification'])
        
        # Map des statuts pour l'affichage
        statut_map = dict(Echange.STATUS_CHOICES)
        
        for echange in echanges:
            writer.writerow([
                echange.date_creation.strftime('%d/%m/%Y'),
                echange.recompense.nom,
                echange.points_utilises,
                statut_map.get(echange.statut, echange.statut),
                echange.date_modification.strftime('%d/%m/%Y')
            ])
        
        return response
    
    except Ambassadeur.DoesNotExist:
        messages.error(request, "Vous n'êtes pas enregistré comme ambassadeur.")
        return redirect('login')