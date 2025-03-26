# authentication/forms.py

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from ambassadeurs.models import Ambassadeur

class CustomAuthenticationForm(AuthenticationForm):
    """
    Formulaire d'authentification personnalisé
    """
    username = forms.CharField(
        label="Identifiant AD",
        widget=forms.TextInput(
            attrs={
                'class': 'appearance-none rounded-md relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm',
                'placeholder': 'Entrez votre identifiant AD',
                'autofocus': True
            }
        )
    )
    
    password = forms.CharField(
        label="Mot de passe",
        strip=False,
        widget=forms.PasswordInput(
            attrs={
                'class': 'appearance-none rounded-md relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm',
                'placeholder': 'Entrez votre mot de passe'
            }
        )
    )

    error_messages = {
        'invalid_login': "Identifiant ou mot de passe invalide.",
        'inactive': "Ce compte a été désactivé.",
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = "Identifiant AD"
        self.fields['password'].label = "Mot de passe"

    def clean(self):
        cleaned_data = super().clean()
        
        # Ici, on pourrait ajouter une validation supplémentaire 
        # pour vérifier si l'utilisateur est bien un ambassadeur
        
        return cleaned_data

class PasswordResetRequestForm(forms.Form):
    """
    Formulaire de demande de réinitialisation de mot de passe
    """
    email = forms.EmailField(
        label="Adresse e-mail",
        widget=forms.EmailInput(
            attrs={
                'class': 'appearance-none rounded-md relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm',
                'placeholder': 'Entrez votre adresse e-mail'
            }
        )
    )
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not User.objects.filter(email=email).exists():
            raise ValidationError("Aucun compte n'est associé à cette adresse e-mail.")
        return email
    
class AssociationCodeForm(forms.Form):
    """
    Formulaire pour associer un utilisateur à son code ambassadeur
    """
    code_ambassadeur = forms.CharField(
        max_length=10,
        widget=forms.TextInput(
            attrs={
                'class': 'appearance-none rounded-md relative block w-full px-3 py-3 border border-gray-300 placeholder-gray-500 text-gray-900 focus:outline-none focus:ring-blue-500 focus:border-blue-500 focus:z-10 sm:text-sm',
                'placeholder': 'Entrez le code qui vous a été attribué'
            }
        )
    )
    
    def clean_code_ambassadeur(self):
        code = self.cleaned_data.get('code_ambassadeur')
        if not Ambassadeur.objects.filter(code_ambassadeur=code, user__isnull=True).exists():
            raise ValidationError("Ce code ambassadeur n'existe pas ou est déjà associé à un utilisateur.")
        return code