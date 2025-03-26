# create_test_data.py

import os
import django
import random
from datetime import datetime, timedelta

# Configurer l'environnement Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'activa_ambassadeurs.settings')
django.setup()

from django.contrib.auth.models import User
from django.utils import timezone
from ambassadeurs.models import Ambassadeur, Police, Points, Exercice, Configuration
from rewards.models import Recompense, Echange, CategorieRecompense
from authentication.models import UserProfile

def create_test_data():
    print("Création des données de test...")
    
    # Créer un exercice
    exercice = Exercice.objects.create(
        nom="Exercice 2025",
        date_debut=datetime(2025, 1, 1).date(),
        date_fin=datetime(2025, 12, 31).date(),
        actif=True
    )
    
    # Créer la configuration
    Configuration.objects.create(
        pourcentage_points=1.5,
        duree_validite_points=365
    )
    
    # Créer des catégories de récompenses
    categories = [
        CategorieRecompense.objects.create(nom="Électronique", ordre=1),
        CategorieRecompense.objects.create(nom="Voyages", ordre=2),
        CategorieRecompense.objects.create(nom="Maison", ordre=3),
        CategorieRecompense.objects.create(nom="Loisirs", ordre=4)
    ]
    
    # Créer des récompenses
    recompenses = [
        Recompense.objects.create(
            nom="Écouteurs sans fil",
            description="Écouteurs Bluetooth premium avec réduction de bruit active",
            categorie=categories[0],
            cout_points=1000,
            quantite_disponible=10,
            actif=True
        ),
        Recompense.objects.create(
            nom="Tablette tactile",
            description="Tablette haute performance avec écran 10 pouces",
            categorie=categories[0],
            cout_points=3500,
            quantite_disponible=5,
            actif=True
        ),
        Recompense.objects.create(
            nom="Week-end pour deux",
            description="Séjour de 2 nuits pour 2 personnes dans un hôtel 4 étoiles",
            categorie=categories[1],
            cout_points=5000,
            quantite_disponible=3,
            actif=True
        ),
        Recompense.objects.create(
            nom="Machine à café",
            description="Machine à café automatique avec broyeur à grains",
            categorie=categories[2],
            cout_points=2000,
            quantite_disponible=8,
            actif=True
        ),
        Recompense.objects.create(
            nom="Abonnement streaming",
            description="Abonnement annuel à un service de streaming premium",
            categorie=categories[3],
            cout_points=800,
            quantite_disponible=-1,
            actif=True
        )
    ]
    
    # Créer des utilisateurs et ambassadeurs
    for i in range(1, 6):
        # Créer l'utilisateur
        username = f"ambassadeur{i}"
        user = User.objects.create_user(
            username=username,
            email=f"{username}@example.com",
            password="password123",
            first_name=f"Prénom{i}",
            last_name=f"NOM{i}"
        )
        
        # Créer le profil
        UserProfile.objects.create(user=user)
        
        # Créer l'ambassadeur
        ambassadeur = Ambassadeur.objects.create(
            user=user,
            code_ambassadeur=f"AA{i:04d}",
            nom_complet=f"{user.first_name} {user.last_name}",
            email=user.email,
            actif=True
        )
        
        # Créer des polices
        for j in range(1, random.randint(3, 8)):
            date_paiement = timezone.now() - timedelta(days=random.randint(1, 180))
            prime_nette = random.randint(500, 10000)
            
            police = Police.objects.create(
                numero_police=f"POL-2025-{i:03d}-{j:03d}",
                ambassadeur=ambassadeur,
                prime_nette=prime_nette,
                statut='payé',
                source_systeme='ORASS' if j % 2 == 0 else 'HELIOS',
                date_paiement=date_paiement
            )
            
            # Les points sont automatiquement créés via le signal dans save() de Police
    
    # Créer un utilisateur admin
    admin_user = User.objects.create_user(
        username="admin",
        email="admin@example.com",
        password="admin123",
        is_staff=True,
        first_name="Admin",
        last_name="SYSTEM"
    )
    
    UserProfile.objects.create(user=admin_user, is_admin=True)
    
    print("Données de test créées avec succès!")
    print("Utilisateurs créés:")
    print("- Admin: username=admin, password=admin123")
    for i in range(1, 6):
        print(f"- Ambassadeur {i}: username=ambassadeur{i}, password=password123")

if __name__ == "__main__":
    create_test_data()
    