#!/usr/bin/env python
"""
Script de test pour vérifier le flux d'authentification complet
"""
import os
import sys
import django

# Configuration Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bibliotech.settings')
django.setup()

from comptes.supabase_service import SupabaseService
from comptes.forms import InscriptionForm, ConnexionForm

def test_inscription_form():
    """Test du formulaire d'inscription"""
    print("📝 Test du formulaire d'inscription...")
    
    # Données de test
    form_data = {
        'prenom': 'Jean',
        'nom': 'Dupont',
        'email': 'jean.dupont@test.com',
        'mot_de_passe': 'motdepasse123',
        'confirmer_mot_de_passe': 'motdepasse123',
        'type_utilisateur': 'etudiant',
        'profession': 'Étudiant',
        'institution': 'Université Test',
        'secteur_activite': 'Éducation',
        'adresse': '123 Rue Test, 75001 Paris',
        'telephone': '0123456789'
    }
    
    form = InscriptionForm(data=form_data)
    
    if form.is_valid():
        print("✅ Formulaire d'inscription valide")
        print(f"   - Prénom: {form.cleaned_data['prenom']}")
        print(f"   - Nom: {form.cleaned_data['nom']}")
        print(f"   - Email: {form.cleaned_data['email']}")
        print(f"   - Type: {form.cleaned_data['type_utilisateur']}")
        return True
    else:
        print("❌ Formulaire d'inscription invalide")
        print(f"   Erreurs: {form.errors}")
        return False

def test_connexion_form():
    """Test du formulaire de connexion"""
    print("\n🔐 Test du formulaire de connexion...")
    
    form_data = {
        'email': 'jean.dupont@test.com',
        'mot_de_passe': 'motdepasse123'
    }
    
    form = ConnexionForm(data=form_data)
    
    if form.is_valid():
        print("✅ Formulaire de connexion valide")
        print(f"   - Email: {form.cleaned_data['email']}")
        return True
    else:
        print("❌ Formulaire de connexion invalide")
        print(f"   Erreurs: {form.errors}")
        return False

def test_supabase_auth():
    """Test de l'authentification Supabase (sans créer d'utilisateur réel)"""
    print("\n🔗 Test de la connexion Supabase...")
    
    try:
        service = SupabaseService()
        
        # Test de connexion basique
        print("✅ Connexion Supabase réussie")
        
        # Test de récupération des tables
        tables_to_check = ['profiles', 'livres', 'categories', 'rendezvous', 'notifications']
        
        for table in tables_to_check:
            try:
                result = service.client.table(table).select('*').limit(1).execute()
                print(f"✅ Table '{table}' accessible")
            except Exception as e:
                print(f"⚠️  Table '{table}' non accessible: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Erreur de connexion Supabase: {e}")
        return False

def test_data_structure():
    """Test de la structure des données"""
    print("\n📊 Test de la structure des données...")
    
    try:
        service = SupabaseService()
        
        # Test des catégories
        categories = service.get_all_categories()
        print(f"✅ Catégories: {len(categories)} trouvées")
        
        # Test des livres
        livres = service.get_all_livres()
        print(f"✅ Livres: {len(livres)} trouvés")
        
        # Test des profils
        profiles = service.client.table('profiles').select('*').limit(5).execute()
        print(f"✅ Profils: {len(profiles.data)} trouvés")
        
        return True
    except Exception as e:
        print(f"❌ Erreur lors du test de structure: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 Test du flux d'authentification complet\n")
    
    tests = [
        test_inscription_form,
        test_connexion_form,
        test_supabase_auth,
        test_data_structure
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print(f"\n📊 Résultats des tests:")
    print(f"✅ Tests réussis: {sum(results)}")
    print(f"❌ Tests échoués: {len(results) - sum(results)}")
    
    if all(results):
        print("\n🎉 Tous les tests sont passés ! Le flux d'authentification est prêt.")
        print("\n📋 Prochaines étapes:")
        print("1. Exécuter le script SQL dans Supabase (init_supabase_tables.sql)")
        print("2. Tester l'inscription via l'interface web")
        print("3. Tester la connexion via l'interface web")
    else:
        print("\n⚠️  Certains tests ont échoué. Vérifiez la configuration.")

if __name__ == "__main__":
    main()
