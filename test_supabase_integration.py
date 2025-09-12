#!/usr/bin/env python
"""
Script de test pour vérifier l'intégration Supabase
"""
import os
import sys
import django

# Configuration Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bibliotech.settings')
django.setup()

from comptes.supabase_service import SupabaseService

def test_supabase_connection():
    """Test de connexion à Supabase"""
    print("🔗 Test de connexion à Supabase...")
    
    try:
        service = SupabaseService()
        print("✅ Connexion Supabase réussie")
        return True
    except Exception as e:
        print(f"❌ Erreur de connexion: {e}")
        return False

def test_auth_operations():
    """Test des opérations d'authentification"""
    print("\n🔐 Test des opérations d'authentification...")
    
    try:
        service = SupabaseService()
        
        # Test de récupération des profils
        profiles = service.client.table('profiles').select('*').limit(5).execute()
        print(f"✅ Récupération des profils: {len(profiles.data)} profils trouvés")
        
        return True
    except Exception as e:
        print(f"❌ Erreur lors des tests d'auth: {e}")
        return False

def test_livres_operations():
    """Test des opérations sur les livres"""
    print("\n📚 Test des opérations sur les livres...")
    
    try:
        service = SupabaseService()
        
        # Test de récupération des livres
        livres = service.get_all_livres()
        print(f"✅ Récupération des livres: {len(livres)} livres trouvés")
        
        # Test de récupération des catégories
        categories = service.get_all_categories()
        print(f"✅ Récupération des catégories: {len(categories)} catégories trouvées")
        
        return True
    except Exception as e:
        print(f"❌ Erreur lors des tests de livres: {e}")
        return False

def test_rendezvous_operations():
    """Test des opérations sur les rendez-vous"""
    print("\n📅 Test des opérations sur les rendez-vous...")
    
    try:
        service = SupabaseService()
        
        # Test de récupération des rendez-vous
        rdv = service.client.table('rendezvous').select('*').limit(5).execute()
        print(f"✅ Récupération des rendez-vous: {len(rdv.data)} RDV trouvés")
        
        return True
    except Exception as e:
        print(f"❌ Erreur lors des tests de rendez-vous: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 Démarrage des tests d'intégration Supabase\n")
    
    tests = [
        test_supabase_connection,
        test_auth_operations,
        test_livres_operations,
        test_rendezvous_operations
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print(f"\n📊 Résultats des tests:")
    print(f"✅ Tests réussis: {sum(results)}")
    print(f"❌ Tests échoués: {len(results) - sum(results)}")
    
    if all(results):
        print("\n🎉 Tous les tests sont passés ! L'intégration Supabase fonctionne correctement.")
    else:
        print("\n⚠️  Certains tests ont échoué. Vérifiez la configuration Supabase.")

if __name__ == "__main__":
    main()
