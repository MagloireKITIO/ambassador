# ambassadeurs/models.py

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal


class Exercice(models.Model):
    """
    Modèle représentant un exercice (période) pour les points des ambassadeurs
    """
    nom = models.CharField(max_length=100)
    date_debut = models.DateField()
    date_fin = models.DateField()
    actif = models.BooleanField(default=True)
    
    def __str__(self):
        return self.nom
    
    class Meta:
        verbose_name = "Exercice"
        verbose_name_plural = "Exercices"

class Ambassadeur(models.Model):
    """
    Modèle représentant un ambassadeur du programme
    """
    TYPE_CHOICES = [
        ('vie', 'Vie'),
        ('non_vie', 'Non-Vie'),
        ('les_deux', 'Vie et Non-Vie'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE,null=True, related_name='ambassadeur')
    type_ambassadeur = models.CharField(max_length=10, choices=TYPE_CHOICES, default='non_vie')
    code_ambassadeur_vie = models.CharField(max_length=20, blank=True, null=True, unique=True)
    code_ambassadeur_non_vie = models.CharField(max_length=20, blank=True, null=True, unique=True)
    nom_complet = models.CharField(max_length=255)
    date_naissance = models.DateField(null=True, blank=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField()
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        if self.type_ambassadeur == 'vie':
            return f"{self.code_ambassadeur_vie} - {self.nom_complet} (Vie)"
        elif self.type_ambassadeur == 'non_vie':
            return f"{self.code_ambassadeur_non_vie} - {self.nom_complet} (Non-Vie)"
        else:
            return f"{self.nom_complet} (Vie et Non-Vie)"
    
    def get_solde_points(self, exercice=None):
        """
        Retourne le solde de points de l'ambassadeur, globalement ou par exercice
        """
        if exercice:
            points_gagnes = self.points_gagnes.filter(exercice=exercice).aggregate(models.Sum('montant'))['montant__sum'] or 0
            points_utilises = self.echanges.filter(exercice=exercice).aggregate(models.Sum('points_utilises'))['points_utilises__sum'] or 0
        else:
            points_gagnes = self.points_gagnes.aggregate(models.Sum('montant'))['montant__sum'] or 0
            points_utilises = self.echanges.aggregate(models.Sum('points_utilises'))['points_utilises__sum'] or 0
        
        return points_gagnes - points_utilises
    
    def get_code_ambassadeur(self):
        """
        Retourne le code ambassadeur en fonction du type d'ambassadeur
        """
        if self.type_ambassadeur == 'vie':
            return self.code_ambassadeur_vie
        elif self.type_ambassadeur == 'non_vie':
            return self.code_ambassadeur_non_vie
        else:
            return f"{self.code_ambassadeur_vie} / {self.code_ambassadeur_non_vie}"
    
    class Meta:
        verbose_name = "Ambassadeur"
        verbose_name_plural = "Ambassadeurs"

class Police(models.Model):
    """
    Modèle représentant une police d'assurance vendue
    """
    TYPE_CHOICES = [
        ('vie', 'Vie'),
        ('non_vie', 'Non-Vie'),
    ]
    
    numero_police = models.CharField(max_length=50, unique=True)
    ambassadeur = models.ForeignKey(Ambassadeur, on_delete=models.CASCADE, related_name='polices')
    type_assurance = models.CharField(max_length=10, choices=TYPE_CHOICES, default='non_vie')
    prime_nette = models.DecimalField(max_digits=10, decimal_places=2)
    statut = models.CharField(max_length=50, default='payé')
    source_systeme = models.CharField(max_length=50, choices=[('ORASS', 'ORASS'), ('HELIOS', 'HELIOS')])
    date_paiement = models.DateField()
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Police {self.numero_police} - {self.get_type_assurance_display()} - {self.ambassadeur.nom_complet}"
    
    def save(self, *args, **kwargs):
        # Vérifier si c'est une nouvelle police
        creation = self.pk is None
        
        # Sauvegarder la police
        super().save(*args, **kwargs)
        
        # Créer automatiquement les points si c'est une nouvelle police avec statut "payé"
        if creation and self.statut == 'payé':
            # Trouver l'exercice correspondant à la date de paiement
            exercice = Exercice.objects.filter(
                date_debut__lte=self.date_paiement,
                date_fin__gte=self.date_paiement,
                actif=True
            ).first()
            
            if exercice:
                # Récupérer le pourcentage de points configuré
                config = Configuration.objects.first()
                if self.type_assurance == 'vie':
                    pourcentage = config.pourcentage_points_vie if config else 1.5
                else:  # 'non_vie'
                    pourcentage = config.pourcentage_points_non_vie if config else 1.5
                
                # Calculer les points
                montant_points = self.prime_nette * (Decimal(pourcentage) / Decimal(100))
                
                # Créer la transaction de points
                Points.objects.create(
                    ambassadeur=self.ambassadeur,
                    police=self,
                    exercice=exercice,
                    type_assurance=self.type_assurance,
                    montant=montant_points,
                    description=f"Points pour la police {self.numero_police}"
                )
    
    class Meta:
        verbose_name = "Police"
        verbose_name_plural = "Polices"

class Points(models.Model):
    """
    Modèle représentant les points gagnés par un ambassadeur
    """
    TYPE_ASSURANCE_CHOICES = [
        ('vie', 'Vie'),
        ('non_vie', 'Non-Vie'),
    ]
    
    ambassadeur = models.ForeignKey(Ambassadeur, on_delete=models.CASCADE, related_name='points_gagnes')
    police = models.ForeignKey(Police, on_delete=models.CASCADE, related_name='points', null=True, blank=True)
    exercice = models.ForeignKey(Exercice, on_delete=models.CASCADE, related_name='points')
    type_assurance = models.CharField(max_length=10, choices=TYPE_ASSURANCE_CHOICES, default='non_vie')
    montant = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.CharField(max_length=255)
    date_expiration = models.DateField(null=True, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.montant} points ({self.get_type_assurance_display()}) pour {self.ambassadeur.nom_complet}"
    
    def save(self, *args, **kwargs):
        # Si la date d'expiration n'est pas définie, calculer en fonction de la configuration
        if not self.date_expiration:
            config = Configuration.objects.first()
            duree_validite = config.duree_validite_points if config else 365  # 1 an par défaut
            
            self.date_expiration = timezone.now().date() + timezone.timedelta(days=duree_validite)
        
        super().save(*args, **kwargs)
    
    class Meta:
        verbose_name = "Points"
        verbose_name_plural = "Points"

class Configuration(models.Model):
    """
    Modèle pour stocker les configurations du programme
    """
    pourcentage_points_vie = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=1.5,
        help_text="Pourcentage de la prime nette converti en points pour l'assurance Vie"
    )
    pourcentage_points_non_vie = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=1.5,
        help_text="Pourcentage de la prime nette converti en points pour l'assurance Non-Vie"
    )
    duree_validite_points = models.IntegerField(
        default=365,
        help_text="Durée de validité des points en jours"
    )
    
    def __str__(self):
        return "Configuration du programme"
    
    class Meta:
        verbose_name = "Configuration"
        verbose_name_plural = "Configurations"