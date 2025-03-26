# rewards/models.py

from django.db import models
from django.utils import timezone
from ambassadeurs.models import Ambassadeur, Exercice

class CategorieRecompense(models.Model):
    """
    Modèle représentant une catégorie de récompense
    """
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    icone = models.ImageField(upload_to='categories/', blank=True, null=True)
    ordre = models.IntegerField(default=0)
    
    def __str__(self):
        return self.nom
    
    class Meta:
        verbose_name = "Catégorie de récompense"
        verbose_name_plural = "Catégories de récompenses"
        ordering = ['ordre', 'nom']

class Recompense(models.Model):
    """
    Modèle représentant une récompense disponible dans le catalogue
    """
    nom = models.CharField(max_length=255)
    description = models.TextField()
    categorie = models.ForeignKey(CategorieRecompense, on_delete=models.CASCADE, related_name='recompenses')
    cout_points = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='recompenses/', blank=True, null=True)
    quantite_disponible = models.IntegerField(default=-1)  # -1 = illimité
    actif = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.nom} ({self.cout_points} points)"
    
    @property
    def est_disponible(self):
        return self.actif and (self.quantite_disponible == -1 or self.quantite_disponible > 0)
    
    class Meta:
        verbose_name = "Récompense"
        verbose_name_plural = "Récompenses"
        ordering = ['cout_points', 'nom']

class Echange(models.Model):
    """
    Modèle représentant un échange de points contre une récompense
    """
    STATUS_CHOICES = [
        ('en_attente', 'En attente'),
        ('confirme', 'Confirmé'),
        ('expedie', 'Expédié'),
        ('livre', 'Livré'),
        ('annule', 'Annulé'),
    ]
    
    ambassadeur = models.ForeignKey(Ambassadeur, on_delete=models.CASCADE, related_name='echanges')
    recompense = models.ForeignKey(Recompense, on_delete=models.CASCADE, related_name='echanges')
    exercice = models.ForeignKey(Exercice, on_delete=models.CASCADE, related_name='echanges')
    points_utilises = models.DecimalField(max_digits=10, decimal_places=2)
    statut = models.CharField(max_length=20, choices=STATUS_CHOICES, default='en_attente')
    commentaire = models.TextField(blank=True, null=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Échange {self.id} par {self.ambassadeur.code_ambassadeur}"
    
    def save(self, *args, **kwargs):
        # Vérifier si c'est un nouvel échange
        creation = self.pk is None
        
        # Sauvegarder l'échange
        super().save(*args, **kwargs)
        
        # Si c'est un nouvel échange confirmé, diminuer la quantité disponible
        if creation and self.statut != 'annule' and self.recompense.quantite_disponible > 0:
            self.recompense.quantite_disponible -= 1
            self.recompense.save()
    
    class Meta:
        verbose_name = "Échange"
        verbose_name_plural = "Échanges"
        ordering = ['-date_creation']