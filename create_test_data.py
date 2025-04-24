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
from backoffice.models import ImportLog

def create_test_data():
    print("Création des données de test...")
    
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
    
    # Créer de nouveaux codes ambassadeurs (sans utilisateurs associés)
    new_ambassadeurs_data = [
        {
            "code_vie": "14530",
            "code_non_vie": "3214",
            "nom_complet": "ESSOMBA MOISE",
            "email": "essomba.moise@group-activa.com",
            "telephone": "699123456",
            "type": "les_deux"
        },
        {
            "code_vie": "15897",
            "code_non_vie": None,
            "nom_complet": "KAMGA ALICE",
            "email": "kamga.alice@group-activa.com",
            "telephone": "699987654",
            "type": "vie"
        },
        {
            "code_vie": None,
            "code_non_vie": "4289",
            "nom_complet": "TAMO PAUL",
            "email": "tamo.paul@group-activa.com",
            "telephone": "699456789",
            "type": "non_vie"
        },
        {
            "code_vie": "16435",
            "code_non_vie": "5012",
            "nom_complet": "FOUDA CLAUDINE",
            "email": "fouda.claudine@group-activa.com",
            "telephone": "699789123",
            "type": "les_deux"
        },
    ]
    
    # Créer des ambassadeurs sans association utilisateur
    created_ambassadeurs = []
    for amb_data in new_ambassadeurs_data:
        code_vie = amb_data["code_vie"]
        code_non_vie = amb_data["code_non_vie"]
        
        # Vérifier si un ambassadeur existe déjà avec ces codes
        ambassadeur_exists = False
        if code_vie:
            ambassadeur_exists = ambassadeur_exists or Ambassadeur.objects.filter(code_ambassadeur_vie=code_vie).exists()
        if code_non_vie:
            ambassadeur_exists = ambassadeur_exists or Ambassadeur.objects.filter(code_ambassadeur_non_vie=code_non_vie).exists()
        
        if ambassadeur_exists:
            print(f"Un ambassadeur avec ces codes existe déjà pour {amb_data['nom_complet']}")
            continue
        
        # Créer l'ambassadeur sans utilisateur associé
        ambassadeur = Ambassadeur.objects.create(
            user=None,  # Pas d'association pour simuler la première connexion
            type_ambassadeur=amb_data["type"],
            code_ambassadeur_vie=code_vie,
            code_ambassadeur_non_vie=code_non_vie,
            nom_complet=amb_data["nom_complet"],
            email=amb_data["email"],
            telephone=amb_data["telephone"],
            actif=True
        )
        created_ambassadeurs.append(ambassadeur)
        print(f"Créé ambassadeur: {ambassadeur.nom_complet} - Type: {ambassadeur.type_ambassadeur}")
    
    # Créer des utilisateurs pour Google Auth (sans association aux ambassadeurs)
    google_users_data = [
        {
            "username": "essomba.moise",
            "email": "essomba.moise@group-activa.com",
            "first_name": "Moise",
            "last_name": "ESSOMBA",
            "password": "password123"
        },
        {
            "username": "kamga.alice",
            "email": "kamga.alice@group-activa.com",
            "first_name": "Alice",
            "last_name": "KAMGA",
            "password": "password123"
        },
        {
            "username": "tamo.paul",
            "email": "tamo.paul@group-activa.com",
            "first_name": "Paul",
            "last_name": "TAMO",
            "password": "password123"
        },
        {
            "username": "fouda.claudine",
            "email": "fouda.claudine@group-activa.com",
            "first_name": "Claudine",
            "last_name": "FOUDA",
            "password": "password123"
        },
    ]
    
    created_users = []
    for user_data in google_users_data:
        username = user_data["username"]
        
        # Vérifier si l'utilisateur existe déjà
        if User.objects.filter(username=username).exists():
            print(f"Utilisateur {username} existe déjà")
            continue
        
        # Créer l'utilisateur
        user = User.objects.create_user(
            username=username,
            email=user_data["email"],
            password=user_data["password"],
            first_name=user_data["first_name"],
            last_name=user_data["last_name"]
        )
        
        # Créer le profil utilisateur
        UserProfile.objects.create(user=user)
        created_users.append(user)
        print(f"Utilisateur {username} créé")
    
    # Créer quelques données d'exemple pour les imports
    # Ces données seront utilisées pour démontrer l'import bimensuel
    if created_ambassadeurs:
        import_sample_entries = []
        current_date = timezone.now().date()
        
        # Pour chaque ambassadeur créé, générer quelques polices d'exemple
        for ambassadeur in created_ambassadeurs:
            if ambassadeur.type_ambassadeur in ['vie', 'les_deux'] and ambassadeur.code_ambassadeur_vie:
                # Polices Vie
                for i in range(1, 4):
                    numero_police = f"VIE-{ambassadeur.code_ambassadeur_vie}-{i:03d}"
                    date_paiement = current_date - timedelta(days=random.randint(1, 30))
                    prime_nette = random.randint(100000, 500000)
                    type_police = random.choice(["Individuel accident", "Épargne", "Retraite", "Capital décès"])
                    
                    import_sample_entries.append({
                        "numero_police": numero_police,
                        "code_ambassadeur": ambassadeur.code_ambassadeur_vie,
                        "prime_nette": prime_nette,
                        "date_paiement": date_paiement.strftime("%d/%m/%Y"),
                        "police": type_police,
                        "nom_ambassadeur": ambassadeur.nom_complet,
                        "type": "vie"
                    })
            
            if ambassadeur.type_ambassadeur in ['non_vie', 'les_deux'] and ambassadeur.code_ambassadeur_non_vie:
                # Polices Non-Vie
                for i in range(1, 4):
                    numero_police = f"NV-{ambassadeur.code_ambassadeur_non_vie}-{i:03d}"
                    date_paiement = current_date - timedelta(days=random.randint(1, 30))
                    prime_nette = random.randint(50000, 300000)
                    type_police = random.choice(["Automobile", "Voyage", "Habitation", "Santé", "Multirisque"])
                    
                    import_sample_entries.append({
                        "numero_police": numero_police,
                        "code_ambassadeur": ambassadeur.code_ambassadeur_non_vie,
                        "prime_nette": prime_nette,
                        "date_paiement": date_paiement.strftime("%d/%m/%Y"),
                        "police": type_police,
                        "nom_ambassadeur": ambassadeur.nom_complet,
                        "type": "non_vie"
                    })
        
        # Afficher un tableau pour l'exemple d'import Vie
        print("\nEXEMPLE D'IMPORT POLICES VIE (HELIOS):")
        print("-" * 80)
        print("{:<20} {:<15} {:<12} {:<12} {:<20} {:<20}".format(
            "numero_police", "code_ambassadeur", "prime_nette", "date_paiement", "police", "Nom de l'ambassadeur"))
        print("-" * 80)
        
        for entry in [e for e in import_sample_entries if e["type"] == "vie"]:
            print("{:<20} {:<15} {:<12} {:<12} {:<20} {:<20}".format(
                entry["numero_police"],
                entry["code_ambassadeur"],
                entry["prime_nette"],
                entry["date_paiement"],
                entry["police"],
                entry["nom_ambassadeur"]
            ))
        
        # Afficher un tableau pour l'exemple d'import Non-Vie
        print("\nEXEMPLE D'IMPORT POLICES NON-VIE (ORASS):")
        print("-" * 80)
        print("{:<20} {:<15} {:<12} {:<12} {:<20} {:<20}".format(
            "numero_police", "code_ambassadeur", "prime_nette", "date_paiement", "police", "Nom de l'ambassadeur"))
        print("-" * 80)
        
        for entry in [e for e in import_sample_entries if e["type"] == "non_vie"]:
            print("{:<20} {:<15} {:<12} {:<12} {:<20} {:<20}".format(
                entry["numero_police"],
                entry["code_ambassadeur"],
                entry["prime_nette"],
                entry["date_paiement"],
                entry["police"],
                entry["nom_ambassadeur"]
            ))
        
        # Exporter les exemples dans des fichiers CSV
        try:
            import csv
            
            # Export Vie
            with open('import_exemple_vie.csv', 'w', newline='') as csvfile:
                fieldnames = ['numero_police', 'code_ambassadeur', 'prime_nette', 'date_paiement', 'police', 'Nom de l\'ambassadeur']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for entry in [e for e in import_sample_entries if e["type"] == "vie"]:
                    writer.writerow({
                        'numero_police': entry["numero_police"],
                        'code_ambassadeur': entry["code_ambassadeur"],
                        'prime_nette': entry["prime_nette"],
                        'date_paiement': entry["date_paiement"],
                        'police': entry["police"],
                        'Nom de l\'ambassadeur': entry["nom_ambassadeur"]
                    })
            
            # Export Non-Vie
            with open('import_exemple_non_vie.csv', 'w', newline='') as csvfile:
                fieldnames = ['numero_police', 'code_ambassadeur', 'prime_nette', 'date_paiement', 'police', 'Nom de l\'ambassadeur']
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                
                writer.writeheader()
                for entry in [e for e in import_sample_entries if e["type"] == "non_vie"]:
                    writer.writerow({
                        'numero_police': entry["numero_police"],
                        'code_ambassadeur': entry["code_ambassadeur"],
                        'prime_nette': entry["prime_nette"],
                        'date_paiement': entry["date_paiement"],
                        'police': entry["police"],
                        'Nom de l\'ambassadeur': entry["nom_ambassadeur"]
                    })
            
            print("\nFichiers CSV créés: import_exemple_vie.csv et import_exemple_non_vie.csv")
        except Exception as e:
            print(f"Erreur lors de la création des fichiers CSV: {str(e)}")
    
    print("\nDonnées de test créées avec succès!")
    print("Utilisateurs pour la première connexion:")
    for user in created_users:
        print(f"- {user.first_name} {user.last_name}: username={user.username}, email={user.email}, password=password123")
    
    print("\nCodes ambassadeurs créés pour test d'association:")
    for ambassadeur in created_ambassadeurs:
        print(f"- {ambassadeur.nom_complet}:")
        if ambassadeur.code_ambassadeur_vie:
            print(f"  - Code Vie: {ambassadeur.code_ambassadeur_vie}")
        if ambassadeur.code_ambassadeur_non_vie:
            print(f"  - Code Non-Vie: {ambassadeur.code_ambassadeur_non_vie}")

if __name__ == "__main__":
    create_test_data()