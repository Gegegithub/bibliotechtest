from supabase import create_client, Client
from django.conf import settings

# Récupération des clés depuis settings.py
SUPABASE_URL = getattr(settings, 'SUPABASE_URL', None)
SUPABASE_KEY = getattr(settings, 'SUPABASE_KEY', None)
SUPABASE_SERVICE_KEY = getattr(settings, 'SUPABASE_SERVICE_ROLE_KEY', None)

if not SUPABASE_URL or not SUPABASE_KEY or not SUPABASE_SERVICE_KEY:
    raise ValueError("Les variables SUPABASE_URL, SUPABASE_KEY et SUPABASE_SERVICE_ROLE_KEY doivent être définies dans settings.py")

# Client Supabase avec clé anonyme (pour les opérations utilisateur)
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Client Supabase avec clé service (pour les opérations admin)
supabase_admin: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)