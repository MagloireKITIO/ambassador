# create_test_data.py

import os
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal

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
    
    # Nettoyer les données existantes (optionnel, à utiliser avec précaution)
    # Décommentez ces lignes si vous voulez supprimer les données existantes
    # User.objects.all().delete()
    # Exercice.objects.all().delete()
    # Configuration.objects.all().delete()
    # CategorieRecompense.objects.all().delete()
    # Recompense.objects.all().delete()
    # Ambassadeur.objects.all().delete()
    
    # Créer un exercice actif s'il n'existe pas
    exercice, created = Exercice.objects.get_or_create(
        nom="Exercice 2025",
        defaults={
            'date_debut': datetime(2025, 1, 1).date(),
            'date_fin': datetime(2025, 12, 31).date(),
            'actif': True
        }
    )
    if created:
        print("Exercice 2025 créé")
    
    # Créer la configuration du programme
    config, created = Configuration.objects.get_or_create(
        pk=1,
        defaults={
            'pourcentage_points_vie': 1.5,
            'pourcentage_points_non_vie': 3.0,
            'duree_validite_points': 365
        }
    )
    if created:
        print("Configuration créée")
    
    # Créer des catégories de récompenses
    categories = []
    for cat_data in [
        {"nom": "Électronique", "ordre": 1},
        {"nom": "Voyages", "ordre": 2},
        {"nom": "Maison", "ordre": 3},
        {"nom": "Loisirs", "ordre": 4}
    ]:
        cat, created = CategorieRecompense.objects.get_or_create(
            nom=cat_data["nom"],
            defaults={'ordre': cat_data["ordre"]}
        )
        categories.append(cat)
        if created:
            print(f"Catégorie {cat.nom} créée")
    
    # Créer des récompenses si elles n'existent pas
    recompenses_data = [
        {
            "nom": "Écouteurs sans fil",
            "description": "Écouteurs Bluetooth premium avec réduction de bruit active",
            "categorie": categories[0],
            "cout_points": 1000,
            "quantite_disponible": 10,
            "actif": True
        },
        {
            "nom": "Tablette tactile",
            "description": "Tablette haute performance avec écran 10 pouces",
            "categorie": categories[0],
            "cout_points": 3500,
            "quantite_disponible": 5,
            "actif": True
        },
        {
            "nom": "Week-end pour deux",
            "description": "Séjour de 2 nuits pour 2 personnes dans un hôtel 4 étoiles",
            "categorie": categories[1],
            "cout_points": 5000,
            "quantite_disponible": 3,
            "actif": True
        },
        {
            "nom": "Machine à café",
            "description": "Machine à café automatique avec broyeur à grains",
            "categorie": categories[2],
            "cout_points": 2000,
            "quantite_disponible": 8,
            "actif": True
        },
        {
            "nom": "Abonnement streaming",
            "description": "Abonnement annuel à un service de streaming premium",
            "categorie": categories[3],
            "cout_points": 800,
            "quantite_disponible": -1,
            "actif": True
        }
    ]
    
    for r_data in recompenses_data:
        recompense, created = Recompense.objects.get_or_create(
            nom=r_data["nom"],
            defaults={
                "description": r_data["description"],
                "categorie": r_data["categorie"],
                "cout_points": r_data["cout_points"],
                "quantite_disponible": r_data["quantite_disponible"],
                "actif": r_data["actif"]
            }
        )
        if created:
            print(f"Récompense {recompense.nom} créée")
    
    # Créer un utilisateur admin s'il n'existe pas
    admin_username = "admin"
    if not User.objects.filter(username=admin_username).exists():
        admin_user = User.objects.create_user(
            username=admin_username,
            email="admin@example.com",
            password="admin123",
            is_staff=True,
            first_name="Admin",
            last_name="SYSTEM"
        )
        UserProfile.objects.create(user=admin_user, is_admin=True)
        print(f"Utilisateur admin créé: {admin_username}/admin123")
    else:
        print(f"Utilisateur admin existe déjà: {admin_username}")
    
    # Créer des utilisateurs "AD" simulés
    ad_users = [
        {
            "username": "tchiat.lazare",
            "password": "password123",
            "email": "tchiat.lazare@activa-assurance.com",
            "first_name": "Lazare",
            "last_name": "TCHIAT",
            "code_vie": "10835",
            "code_non_vie": "1823",
            "telephone": "699949714",
            "type": "les_deux"
        },
        {
            "username": "kopipie.carine",
            "password": "password123",
            "email": "kopipie.carine@activa-assurance.com",
            "first_name": "Carine",
            "last_name": "KOPIPIE DJINGOU",
            "code_vie": "12009",
            "code_non_vie": "2517",
            "telephone": "699976322",
            "type": "les_deux"
        },
        {
            "username": "mbime.martin",
            "password": "password123",
            "email": "mbime.martin@activa-assurance.com",
            "first_name": "Martin",
            "last_name": "MBIME EBWEA",
            "code_vie": "10833",
            "code_non_vie": "1866",
            "telephone": "694395585",
            "type": "vie"
        },
        {
            "username": "ganapou.bernard",
            "password": "password123",
            "email": "ganapou.bernard@activa-assurance.com",
            "first_name": "Bernard",
            "last_name": "GANAPOU",
            "code_vie": None,
            "code_non_vie": "756",
            "telephone": "696705451",
            "type": "non_vie"
        }
    ]
    
    # Créer des utilisateurs "AD" et des codes ambassadeurs (sans association)
    for user_data in ad_users:
        username = user_data["username"]
        
        # Vérifier si l'utilisateur existe déjà
        if User.objects.filter(username=username).exists():
            print(f"Utilisateur {username} existe déjà")
            user = User.objects.get(username=username)
        else:
            # Créer l'utilisateur
            user = User.objects.create_user(
                username=username,
                email=user_data["email"],
                password=user_data["password"],
                first_name=user_data["first_name"],
                last_name=user_data["last_name"]
            )
            # Créer le profil
            UserProfile.objects.create(user=user)
            print(f"Utilisateur {username} créé")
        
        # Vérifier si un ambassadeur existe avec ces codes
        code_vie = user_data["code_vie"]
        code_non_vie = user_data["code_non_vie"]
        
        ambassadeur_exists = False
        if code_vie:
            ambassadeur_exists = ambassadeur_exists or Ambassadeur.objects.filter(code_ambassadeur_vie=code_vie).exists()
        if code_non_vie:
            ambassadeur_exists = ambassadeur_exists or Ambassadeur.objects.filter(code_ambassadeur_non_vie=code_non_vie).exists()
        
        if ambassadeur_exists:
            print(f"Un ambassadeur avec ces codes existe déjà")
            continue
        
        # Créer l'ambassadeur sans l'associer à l'utilisateur
        type_ambassadeur = user_data["type"]
        nom_complet = f"{user_data['first_name']} {user_data['last_name']}"
        
        ambassadeur = Ambassadeur.objects.create(
            user=None,  # Pas d'association pour simuler la première connexion
            type_ambassadeur=type_ambassadeur,
            code_ambassadeur_vie=code_vie,
            code_ambassadeur_non_vie=code_non_vie,
            nom_complet=nom_complet,
            email=user_data["email"],
            telephone=user_data["telephone"],
            actif=True
        )
        
        print(f"Créé ambassadeur: {nom_complet} - Type: {type_ambassadeur}")
        
        # Pour démonstration, associer un des ambassadeurs à son utilisateur
        if user_data["username"] == "ganapou.bernard":
            ambassadeur.user = user
            ambassadeur.save()
            print(f"Associé {nom_complet} à son utilisateur")
    
    # Créer des polices pour l'ambassadeur associé
    try:
        ambassadeur_associe = Ambassadeur.objects.get(user__username="ganapou.bernard")
        
        # Vérifier si des polices existent déjà
        if Police.objects.filter(ambassadeur=ambassadeur_associe).exists():
            print(f"Des polices existent déjà pour {ambassadeur_associe.nom_complet}")
        else:
            # Polices Non-Vie
            for i in range(1, 5):
                date_paiement = timezone.now() - timedelta(days=i*15)
                prime_nette = random.randint(500, 10000)
                
                Police.objects.create(
                    numero_police=f"NV-2025-{i:03d}",
                    ambassadeur=ambassadeur_associe,
                    type_assurance='non_vie',
                    prime_nette=prime_nette,
                    statut='payé',
                    source_systeme='ORASS',
                    date_paiement=date_paiement
                )
                
            print(f"Créé des polices Non-Vie pour {ambassadeur_associe.nom_complet}")
    except Ambassadeur.DoesNotExist:
        print("Aucun ambassadeur associé trouvé")
    
    print("Données de test créées avec succès!")
    print("Utilisateurs créés:")
    print("- Admin: username=admin, password=admin123")
    for user_data in ad_users:
        status = "Associé" if user_data["username"] == "ganapou.bernard" else "Non associé"
        print(f"- Ambassadeur {user_data['first_name']} {user_data['last_name']}: username={user_data['username']}, password={user_data['password']}, statut={status}")

if __name__ == "__main__":
    create_test_data()