#!/usr/bin/env python
import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bibliotech.settings')
django.setup()

from comptes.supabase_service import SupabaseService

def test_redirections():
    """Test des redirections selon le type d'utilisateur"""
    service = SupabaseService()
    
    # Test 1: Utilisateur normal (étudiant)
    print("=== Test 1: Utilisateur normal ===")
    test_data_normal = {
        "nom": "Normal",
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
    email_normal = f"normal{int(time.time())}@example.com"
    password = "test123"
    
    print(f"Inscription: {email_normal}")
    result = service.sign_up(email_normal, password, test_data_normal)
    
    if result['success']:
        print("✅ Inscription réussie!")
        profile = result['profile']
        print(f"Type: {profile.get('profil', 'N/A')}")
        print(f"is_librarian: {profile.get('is_librarian', False)}")
        print(f"is_admin: {profile.get('is_admin', False)}")
        
        # Test de connexion et redirection
        login_result = service.sign_in(email_normal, password)
        if login_result['success']:
            print("✅ Connexion réussie!")
            profile = login_result['profile']
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
    
    print("\n" + "="*50 + "\n")
    
    # Test 2: Bibliothécaire
    print("=== Test 2: Bibliothécaire ===")
    test_data_librarian = {
        "nom": "Librarian",
        "prenom": "Test",
        "adresse": "456 Library Street",
        "telephone": "0987654321",
        "secteur_activite": "Library",
        "institution": "Test Library",
        "profil": "bibliothecaire",
        "is_admin": False,
        "is_administration": False,
        "is_librarian": True,
        "is_user": True
    }
    
    email_librarian = f"librarian{int(time.time())}@example.com"
    
    print(f"Inscription: {email_librarian}")
    result = service.sign_up(email_librarian, password, test_data_librarian)
    
    if result['success']:
        print("✅ Inscription réussie!")
        profile = result['profile']
        print(f"Type: {profile.get('profil', 'N/A')}")
        print(f"is_librarian: {profile.get('is_librarian', False)}")
        print(f"is_admin: {profile.get('is_admin', False)}")
        
        # Test de connexion et redirection
        login_result = service.sign_in(email_librarian, password)
        if login_result['success']:
            print("✅ Connexion réussie!")
            profile = login_result['profile']
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
    test_redirections()
