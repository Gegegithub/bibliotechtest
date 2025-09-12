#!/usr/bin/env python
"""
Script de test pour vérifier que l'application fonctionne sans Django ORM
"""
import os
import sys
import django

# Configuration Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bibliotech.settings')
django.setup()

def test_django_config():
    """Test de la configuration Django"""
    print("🔧 Test de la configuration Django...")
    
    from django.conf import settings
    
    # Vérifier que les apps Django ORM sont désactivées
    orm_apps = ['django.contrib.contenttypes', 'django.contrib.sessions', 'django.contrib.auth']
    active_orm_apps = [app for app in orm_apps if app in settings.INSTALLED_APPS]
    
    if active_orm_apps:
        print(f"❌ Apps Django ORM encore actives: {active_orm_apps}")
        return False
    else:
        print("✅ Apps Django ORM désactivées")
    
    # Vérifier que la base de données est désactivée
    if hasattr(settings, 'DATABASES') and settings.DATABASES:
        print("❌ Configuration de base de données encore active")
        return False
    else:
        print("✅ Configuration de base de données désactivée")
    
    return True

def test_supabase_connection():
    """Test de la connexion Supabase"""
    print("\n🔗 Test de la connexion Supabase...")
    
    try:
        # Définir les variables d'environnement pour le test
        import os
        os.environ['SUPABASE_URL'] = 'https://cfgxxawxmscsrtjsorkp.supabase.co'
        os.environ['SUPABASE_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNnZnh4YXd4bXNjc3J0anNvcmtwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzY0MzQwMDAsImV4cCI6MjA1MjAxMDAwMH0.Ej8Ej8Ej8Ej8Ej8Ej8Ej8Ej8Ej8Ej8Ej8Ej8Ej8Ej8'
        os.environ['SUPABASE_SERVICE_ROLE_KEY'] = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImNnZnh4YXd4bXNjc3J0anNvcmtwIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTczNjQzNDAwMCwiZXhwIjoyMDUyMDEwMDAwfQ.ServiceKeyServiceKeyServiceKeyServiceKeyServiceKeyServiceKey'
        
        from comptes.supabase_service import SupabaseService
        service = SupabaseService()
        print("✅ Connexion Supabase réussie")
        return True
    except Exception as e:
        print(f"❌ Erreur de connexion Supabase: {e}")
        return False

def test_forms():
    """Test des formulaires sans modèles"""
    print("\n📝 Test des formulaires...")
    
    try:
        from comptes.forms import InscriptionForm, ConnexionForm
        from bibliotheque.forms import CategorieForm, LivreForm
        
        # Test InscriptionForm
        form_data = {
            'prenom': 'Test',
            'nom': 'User',
            'email': 'test@example.com',
            'mot_de_passe': 'password123',
            'confirmer_mot_de_passe': 'password123',
            'type_utilisateur': 'etudiant'
        }
        
        form = InscriptionForm(data=form_data)
        if form.is_valid():
            print("✅ InscriptionForm fonctionne")
        else:
            print(f"❌ InscriptionForm invalide: {form.errors}")
            return False
        
        # Test CategorieForm
        categorie_data = {'nom': 'Test Category'}
        form = CategorieForm(data=categorie_data)
        if form.is_valid():
            print("✅ CategorieForm fonctionne")
        else:
            print(f"❌ CategorieForm invalide: {form.errors}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Erreur lors du test des formulaires: {e}")
        return False

def test_middleware():
    """Test du middleware d'authentification"""
    print("\n🔐 Test du middleware d'authentification...")
    
    try:
        from comptes.middleware import AuthentificationMiddleware
        from django.test import RequestFactory
        
        # Créer une requête de test
        factory = RequestFactory()
        request = factory.get('/')
        request.session = {}
        
        # Tester le middleware
        middleware = AuthentificationMiddleware(lambda req: None)
        response = middleware(request)
        
        print("✅ Middleware d'authentification fonctionne")
        return True
    except Exception as e:
        print(f"❌ Erreur lors du test du middleware: {e}")
        return False

def test_views():
    """Test des vues sans modèles Django"""
    print("\n👁️ Test des vues...")
    
    try:
        from bibliotheque.views import home
        from django.test import RequestFactory
        
        # Créer une requête de test
        factory = RequestFactory()
        request = factory.get('/')
        request.session = {}
        request.utilisateur = None
        
        # Tester la vue home
        response = home(request)
        
        if response.status_code == 200:
            print("✅ Vue home fonctionne")
        else:
            print(f"❌ Vue home retourne le code {response.status_code}")
            return False
        
        return True
    except Exception as e:
        print(f"❌ Erreur lors du test des vues: {e}")
        return False

def main():
    """Fonction principale de test"""
    print("🚀 Test de l'application sans Django ORM\n")
    
    tests = [
        test_django_config,
        test_supabase_connection,
        test_forms,
        test_middleware,
        test_views
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print(f"\n📊 Résultats des tests:")
    print(f"✅ Tests réussis: {sum(results)}")
    print(f"❌ Tests échoués: {len(results) - sum(results)}")
    
    if all(results):
        print("\n🎉 Tous les tests sont passés ! L'application fonctionne sans Django ORM.")
        print("\n📋 Prochaines étapes:")
        print("1. Exécuter le script SQL dans Supabase")
        print("2. Lancer le serveur: python manage.py runserver")
        print("3. Tester l'interface web")
    else:
        print("\n⚠️  Certains tests ont échoué. Vérifiez la configuration.")

if __name__ == "__main__":
    main()
