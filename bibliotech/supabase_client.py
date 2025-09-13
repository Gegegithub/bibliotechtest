from django.conf import settings
import logging

# Configuration du logging
logger = logging.getLogger(__name__)

# Récupération des clés depuis settings.py
SUPABASE_URL = getattr(settings, 'SUPABASE_URL', None)
SUPABASE_KEY = getattr(settings, 'SUPABASE_KEY', None)
SUPABASE_SERVICE_KEY = getattr(settings, 'SUPABASE_SERVICE_ROLE_KEY', None)

# Variables globales pour les clients
supabase = None
supabase_admin = None

def init_supabase_clients():
    """Initialise les clients Supabase avec gestion d'erreur"""
    global supabase, supabase_admin
    
    if not SUPABASE_URL or not SUPABASE_KEY or not SUPABASE_SERVICE_KEY:
        logger.error("Les variables SUPABASE_URL, SUPABASE_KEY et SUPABASE_SERVICE_ROLE_KEY doivent être définies dans settings.py")
        return False
    
    try:
        from supabase import create_client, Client
        
        # Client Supabase avec clé anonyme (pour les opérations utilisateur)
        supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Client Supabase avec clé service (pour les opérations admin)
        supabase_admin = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        
        logger.info("Clients Supabase initialisés avec succès")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'initialisation des clients Supabase: {e}")
        return False

# Initialiser les clients au chargement du module
init_supabase_clients()