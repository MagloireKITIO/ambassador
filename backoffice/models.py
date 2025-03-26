# backoffice/models.py

from django.db import models
from django.contrib.auth.models import User

class ImportLog(models.Model):
    """
    Modèle pour suivre les importations de données
    """
    SOURCE_CHOICES = [
        ('ORASS', 'ORASS'),
        ('HELIOS', 'HELIOS'),
        ('RH', 'Ressources Humaines'),
        ('MANUEL', 'Import manuel'),
    ]
    
    source = models.CharField(max_length=50, choices=SOURCE_CHOICES)
    fichier = models.FileField(upload_to='imports/', null=True, blank=True)
    utilisateur = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='imports')
    date_import = models.DateTimeField(auto_now_add=True)
    nombre_enregistrements = models.IntegerField(default=0)
    reussi = models.BooleanField(default=False)
    message_erreur = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"Import {self.source} du {self.date_import}"
    
    class Meta:
        verbose_name = "Journal d'importation"
        verbose_name_plural = "Journal des importations"
        ordering = ['-date_import']

class Notification(models.Model):
    """
    Modèle pour les notifications système
    """
    NIVEAU_CHOICES = [
        ('info', 'Information'),
        ('success', 'Succès'),
        ('warning', 'Avertissement'),
        ('error', 'Erreur'),
    ]
    
    titre = models.CharField(max_length=255)
    message = models.TextField()
    niveau = models.CharField(max_length=20, choices=NIVEAU_CHOICES, default='info')
    destinataire = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', null=True, blank=True)
    pour_tous = models.BooleanField(default=False)
    lue = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_expiration = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return self.titre
    
    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-date_creation']

class SystemeConfiguration(models.Model):
    """
    Modèle pour les configurations générales du système
    """
    cle = models.CharField(max_length=100, unique=True)
    valeur = models.TextField()
    description = models.TextField(blank=True, null=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.cle
    
    class Meta:
        verbose_name = "Configuration système"
        verbose_name_plural = "Configurations système"
        ordering = ['cle']