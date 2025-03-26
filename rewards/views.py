# rewards/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse
from ambassadeurs.models import Ambassadeur, Exercice
from .models import Recompense, CategorieRecompense, Echange

@login_required
def catalogue(request):
    """
    Vue pour afficher le catalogue des récompenses
    """
    try:
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
        
        # Récupérer le solde de points disponible
        points_disponibles = ambassadeur.get_solde_points(exercice_actif)
        
        # Filtrer par catégorie si spécifié
        categorie_id = request.GET.get('categorie')
        if categorie_id:
            categorie = get_object_or_404(CategorieRecompense, pk=categorie_id)
            recompenses = Recompense.objects.filter(categorie=categorie, actif=True)
        else:
            recompenses = Recompense.objects.filter(actif=True)
        
        # Filtrer par recherche si spécifié
        recherche = request.GET.get('recherche')
        if recherche:
            recompenses = recompenses.filter(
                Q(nom__icontains=recherche) | Q(description__icontains=recherche)
            )
        
        # Filtrer par points disponibles si spécifié
        points_filter = request.GET.get('points')
        if points_filter == 'disponibles':
            recompenses = recompenses.filter(cout_points__lte=points_disponibles)
        
        # Trier par prix
        tri = request.GET.get('tri', 'asc')
        if tri == 'asc':
            recompenses = recompenses.order_by('cout_points')
        else:
            recompenses = recompenses.order_by('-cout_points')
        
        # Récupérer toutes les catégories pour le filtre
        categories = CategorieRecompense.objects.all().order_by('ordre')
        
        context = {
            'ambassadeur': ambassadeur,
            'recompenses': recompenses,
            'categories': categories,
            'categorie_selectionnee': categorie_id,
            'points_disponibles': points_disponibles,
            'exercice_actif': exercice_actif,
            'recherche': recherche,
            'points_filter': points_filter,
            'tri': tri,
        }
        
        return render(request, 'rewards/catalogue.html', context)
    
    except Ambassadeur.DoesNotExist:
        messages.error(request, "Vous n'êtes pas enregistré comme ambassadeur.")
        return redirect('login')

@login_required
def detail_recompense(request, recompense_id):
    """
    Vue pour afficher les détails d'une récompense
    """
    try:
        ambassadeur = Ambassadeur.objects.get(user=request.user)
        recompense = get_object_or_404(Recompense, pk=recompense_id, actif=True)
        
        # Récupérer l'exercice actif
        exercice_actif = Exercice.objects.filter(
            date_debut__lte=timezone.now().date(),
            date_fin__gte=timezone.now().date(),
            actif=True
        ).first()
        
        if not exercice_actif:
            # Si aucun exercice actif, prendre le plus récent
            exercice_actif = Exercice.objects.filter(actif=True).order_by('-date_debut').first()
        
        # Récupérer le solde de points disponible
        points_disponibles = ambassadeur.get_solde_points(exercice_actif)
        
        # Vérifier si l'ambassadeur a assez de points
        peut_echanger = points_disponibles >= recompense.cout_points
        
        context = {
            'ambassadeur': ambassadeur,
            'recompense': recompense,
            'points_disponibles': points_disponibles,
            'exercice_actif': exercice_actif,
            'peut_echanger': peut_echanger,
        }
        
        return render(request, 'rewards/detail_recompense.html', context)
    
    except Ambassadeur.DoesNotExist:
        messages.error(request, "Vous n'êtes pas enregistré comme ambassadeur.")
        return redirect('login')

@login_required
def echanger_recompense(request, recompense_id):
    """
    Vue pour échanger des points contre une récompense
    """
    if request.method != 'POST':
        return redirect('catalogue')
    
    try:
        ambassadeur = Ambassadeur.objects.get(user=request.user)
        recompense = get_object_or_404(Recompense, pk=recompense_id, actif=True)
        
        # Récupérer l'exercice actif
        exercice_actif = Exercice.objects.filter(
            date_debut__lte=timezone.now().date(),
            date_fin__gte=timezone.now().date(),
            actif=True
        ).first()
        
        if not exercice_actif:
            messages.error(request, "Aucun exercice actif trouvé.")
            return redirect('detail_recompense', recompense_id=recompense_id)
        
        # Récupérer le solde de points disponible
        points_disponibles = ambassadeur.get_solde_points(exercice_actif)
        
        # Vérifier si l'ambassadeur a assez de points
        if points_disponibles < recompense.cout_points:
            messages.error(request, "Vous n'avez pas assez de points pour cette récompense.")
            return redirect('detail_recompense', recompense_id=recompense_id)
        
        # Vérifier si la récompense est disponible en stock
        if recompense.quantite_disponible == 0:
            messages.error(request, "Cette récompense n'est plus disponible en stock.")
            return redirect('detail_recompense', recompense_id=recompense_id)
        
        # Créer l'échange
        commentaire = request.POST.get('commentaire', '')
        
        echange = Echange.objects.create(
            ambassadeur=ambassadeur,
            recompense=recompense,
            exercice=exercice_actif,
            points_utilises=recompense.cout_points,
            commentaire=commentaire,
            statut='en_attente'
        )
        
        messages.success(request, "Votre demande d'échange a été soumise avec succès !")
        return redirect('historique_echanges')
    
    except Ambassadeur.DoesNotExist:
        messages.error(request, "Vous n'êtes pas enregistré comme ambassadeur.")
        return redirect('login')

@login_required
def annuler_echange(request, echange_id):
    """
    Vue pour annuler un échange en attente
    """
    if request.method != 'POST':
        return redirect('historique_echanges')
    
    try:
        ambassadeur = Ambassadeur.objects.get(user=request.user)
        echange = get_object_or_404(Echange, pk=echange_id, ambassadeur=ambassadeur)
        
        # Vérifier si l'échange peut être annulé
        if echange.statut not in ['en_attente', 'confirme']:
            messages.error(request, "Cet échange ne peut plus être annulé.")
            return redirect('historique_echanges')
        
        # Annuler l'échange
        echange.statut = 'annule'
        echange.save()
        
        messages.success(request, "Votre échange a été annulé avec succès.")
        return redirect('historique_echanges')
    
    except Ambassadeur.DoesNotExist:
        messages.error(request, "Vous n'êtes pas enregistré comme ambassadeur.")
        return redirect('login')

@login_required
def verifier_points(request):
    """
    API pour vérifier les points disponibles
    """
    try:
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
        
        # Récupérer le solde de points disponible
        points_disponibles = ambassadeur.get_solde_points(exercice_actif)
        
        return JsonResponse({
            'points_disponibles': points_disponibles,
            'exercice': exercice_actif.nom if exercice_actif else None,
        })
    
    except Ambassadeur.DoesNotExist:
        return JsonResponse({'error': "Utilisateur non enregistré comme ambassadeur."}, status=403)