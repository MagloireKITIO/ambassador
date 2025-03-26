# authentication/models.py

from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    """
    Modèle pour étendre le modèle User par défaut de Django
    """
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    is_admin = models.BooleanField(default=False)
    last_login_ip = models.GenericIPAddressField(null=True, blank=True)
    
    def __str__(self):
        return f"Profil de {self.user.username}"
    
    class Meta:
        verbose_name = "Profil utilisateur"
        verbose_name_plural = "Profils utilisateurs"

class LoginLog(models.Model):
    """
    Modèle pour suivre les connexions des utilisateurs
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_logs')
    login_time = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True, null=True)
    is_successful = models.BooleanField(default=True)
    
    def __str__(self):
        status = "réussie" if self.is_successful else "échouée"
        return f"Connexion {status} de {self.user.username} le {self.login_time}"
    
    class Meta:
        verbose_name = "Journal de connexion"
        verbose_name_plural = "Journal des connexions"
        ordering = ['-login_time']