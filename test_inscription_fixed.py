#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bibliotech.settings')
django.setup()

from comptes.supabase_service import SupabaseService

def test_inscription_fixed():
    """Test d'inscription après correction de la fonction handle_new_user"""
    service = SupabaseService()
    
    # Données de test
    test_data = {
        "nom": "Test",
        "prenom": "User",
        "adresse": "123 Test Street",
        "telephone": "1234567890",
        "secteur_activite": "Education",
        "institution": "Test University",
        "profil": "etudiant",
        "is_admin": False,
        "is_administration": False,
        "is_librarian": False,
        "is_user": True
    }
    
    import time
    email = f"test{int(time.time())}@example.com"
    password = "testpassword123"
    
    print(f"Test d'inscription pour: {email}")
    print(f"Données: {test_data}")
    
    result = service.sign_up(email, password, test_data)
    
    if result['success']:
        print("✅ Inscription réussie!")
        print(f"User ID: {result['user'].id}")
        print(f"Profile: {result['profile']}")
        
        # Test de connexion immédiat
        print("\n--- Test de connexion ---")
        login_result = service.sign_in(email, password)
        if login_result['success']:
            print("✅ Connexion réussie!")
            profile = login_result['profile']
            print(f"Type d'utilisateur: {profile.get('profil', 'N/A')}")
            print(f"is_librarian: {profile.get('is_librarian', False)}")
            print(f"is_admin: {profile.get('is_admin', False)}")
            
            # Test de redirection selon le type
            if profile.get('is_librarian'):
                print("→ Redirection vers: Dashboard Bibliothécaire")
            elif profile.get('is_admin'):
                print("→ Redirection vers: Dashboard Admin")
            else:
                print("→ Redirection vers: Accueil")
        else:
            print(f"❌ Erreur de connexion: {login_result['error']}")
    else:
        print(f"❌ Erreur d'inscription: {result['error']}")

if __name__ == "__main__":
    test_inscription_fixed()
