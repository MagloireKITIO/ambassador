# backoffice/forms.py

from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from ambassadeurs.models import Exercice, Configuration
from rewards.models import Recompense, CategorieRecompense

class ImportForm(forms.Form):
    """
    Formulaire pour l'import de données
    """
    SOURCE_CHOICES = [
        ('ORASS', 'ORASS'),
        ('HELIOS', 'HELIOS'),
        ('RH', 'Ressources Humaines'),
    ]
    
    source = forms.ChoiceField(
        choices=SOURCE_CHOICES,
        widget=forms.Select(attrs={'class': 'block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm'})
    )
    
    fichier = forms.FileField(
        widget=forms.FileInput(attrs={'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100'})
    )
    
    def clean_fichier(self):
        fichier = self.cleaned_data.get('fichier')
        
        # Vérifier l'extension du fichier
        if not fichier.name.endswith('.csv'):
            raise ValidationError("Le fichier doit être au format CSV.")
        
        return fichier

class ExerciceForm(forms.ModelForm):
    """
    Formulaire pour la gestion des exercices
    """
    class Meta:
        model = Exercice
        fields = ['nom', 'date_debut', 'date_fin', 'actif']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm'}),
            'date_debut': forms.DateInput(attrs={'class': 'block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm', 'type': 'date'}),
            'date_fin': forms.DateInput(attrs={'class': 'block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm', 'type': 'date'}),
            'actif': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get('date_debut')
        date_fin = cleaned_data.get('date_fin')
        
        # Vérifier que la date de fin est après la date de début
        if date_debut and date_fin and date_debut >= date_fin:
            raise ValidationError("La date de fin doit être postérieure à la date de début.")
        
        return cleaned_data

class ConfigurationForm(forms.ModelForm):
    """
    Formulaire pour la configuration du programme
    """
    class Meta:
        model = Configuration
        fields = ['pourcentage_points_vie', 'pourcentage_points_non_vie', 'duree_validite_points']
        widgets = {
            'pourcentage_points_vie': forms.NumberInput(attrs={'class': 'block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm', 'step': '0.1'}),
            'pourcentage_points_non_vie': forms.NumberInput(attrs={'class': 'block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm', 'step': '0.1'}),
            'duree_validite_points': forms.NumberInput(attrs={'class': 'block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm'}),
        }
    
    def clean_pourcentage_points_vie(self):
        pourcentage = self.cleaned_data.get('pourcentage_points_vie')
        
        # Vérifier que le pourcentage est positif
        if pourcentage <= 0:
            raise ValidationError("Le pourcentage pour la Vie doit être supérieur à 0.")
        
        return pourcentage
    
    def clean_pourcentage_points_non_vie(self):
        pourcentage = self.cleaned_data.get('pourcentage_points_non_vie')
        
        # Vérifier que le pourcentage est positif
        if pourcentage <= 0:
            raise ValidationError("Le pourcentage pour la Non-Vie doit être supérieur à 0.")
        
        return pourcentage
    
    def clean_duree_validite_points(self):
        duree = self.cleaned_data.get('duree_validite_points')
        
        # Vérifier que la durée est positive
        if duree <= 0:
            raise ValidationError("La durée de validité doit être supérieure à 0.")
        
        return duree

class RecompenseForm(forms.ModelForm):
    """
    Formulaire pour la gestion des récompenses
    """
    class Meta:
        model = Recompense
        fields = ['nom', 'description', 'categorie', 'cout_points', 'image', 'quantite_disponible', 'actif']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm'}),
            'description': forms.Textarea(attrs={'class': 'block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm', 'rows': 3}),
            'categorie': forms.Select(attrs={'class': 'block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm'}),
            'cout_points': forms.NumberInput(attrs={'class': 'block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm', 'step': '0.1'}),
            'image': forms.FileInput(attrs={'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100'}),
            'quantite_disponible': forms.NumberInput(attrs={'class': 'block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm'}),
            'actif': forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'}),
        }
    
    def clean_cout_points(self):
        cout = self.cleaned_data.get('cout_points')
        
        # Vérifier que le coût est positif
        if cout <= 0:
            raise ValidationError("Le coût en points doit être supérieur à 0.")
        
        return cout

class CategorieRecompenseForm(forms.ModelForm):
    """
    Formulaire pour la gestion des catégories de récompenses
    """
    class Meta:
        model = CategorieRecompense
        fields = ['nom', 'description', 'icone', 'ordre']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm'}),
            'description': forms.Textarea(attrs={'class': 'block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm', 'rows': 2}),
            'icone': forms.FileInput(attrs={'class': 'block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100'}),
            'ordre': forms.NumberInput(attrs={'class': 'block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm'}),
        }

class NotificationForm(forms.Form):
    """
    Formulaire pour créer des notifications
    """
    NIVEAU_CHOICES = [
        ('info', 'Information'),
        ('success', 'Succès'),
        ('warning', 'Avertissement'),
        ('error', 'Erreur'),
    ]
    
    titre = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'class': 'block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm'})
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm', 'rows': 3})
    )
    
    niveau = forms.ChoiceField(
        choices=NIVEAU_CHOICES,
        widget=forms.Select(attrs={'class': 'block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm'})
    )
    
    pour_tous = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={'class': 'h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded'})
    )
    
    date_expiration = forms.DateField(
        required=True,
        widget=forms.DateInput(attrs={'class': 'block w-full py-2 px-3 border border-gray-300 bg-white rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm', 'type': 'date'})
    )
    
    def clean_date_expiration(self):
        date_expiration = self.cleaned_data.get('date_expiration')
        
        # Vérifier que la date d'expiration est future
        if date_expiration and date_expiration < timezone.now().date():
            raise ValidationError("La date d'expiration doit être dans le futur.")
        
        return date_expiration