from django import template
from comptes.supabase_service import SupabaseService

register = template.Library()

@register.filter
def first_utilisateur_id(value):
    """
    Retourne l'ID du premier utilisateur inscrit
    """
    try:
        supabase_service = SupabaseService()
        # Récupérer le premier utilisateur par date d'inscription
        result = supabase_service.client.table('profiles').select('id').order('created_at', desc=False).limit(1).execute()
        if result.data:
            return result.data[0]['id']
    except Exception as e:
        print(f"Erreur lors de la récupération du premier utilisateur: {e}")
    return None

@register.filter
def is_super_admin(utilisateur):
    """
    Vérifie si l'utilisateur est le super administrateur (premier inscrit)
    """
    try:
        supabase_service = SupabaseService()
        # Récupérer le premier utilisateur par date d'inscription
        result = supabase_service.client.table('profiles').select('id').order('created_at', desc=False).limit(1).execute()
        if result.data and utilisateur:
            premier_id = result.data[0]['id']
            return utilisateur.get('id') == premier_id
    except Exception as e:
        print(f"Erreur lors de la vérification du super admin: {e}")
    return False
