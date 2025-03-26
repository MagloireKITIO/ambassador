# run_project.py

import os
import subprocess
import sys

def run_project():
    # Installer les dépendances
    print("Installation des dépendances...")
    subprocess.call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    
    # Vérifier si la base de données existe
    if not os.path.exists("db.sqlite3"):
        print("Initialisation de la base de données...")
        subprocess.call([sys.executable, "manage.py", "migrate"])
        
        # Créer des données de test
        print("Création des données de test...")
        subprocess.call([sys.executable, "create_test_data.py"])
    
    # Lancer le serveur
    print("Démarrage du serveur...")
    subprocess.call([sys.executable, "manage.py", "runserver"])

if __name__ == "__main__":
    run_project()