from django.shortcuts import redirect
from django.contrib import messages
from .supabase_service import SupabaseService
from functools import wraps

class AuthentificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Vérifier si l'utilisateur est connecté via Supabase
        utilisateur_id = request.session.get('utilisateur_id')
        if utilisateur_id:
            try:
                # Récupérer le profil depuis Supabase
                supabase_service = SupabaseService()
                profile = supabase_service.get_profile_by_id(utilisateur_id)
                
                if profile:
                    # Créer un objet utilisateur simulé pour la compatibilité
                    request.utilisateur = type('Utilisateur', (), {
                        'id': profile['id'],
                        'email': profile['email'],
                        'nom': profile['nom'],
                        'prenom': profile['prenom'],
                        'est_bibliothecaire': profile.get('is_librarian', False),
                        'est_personnel': profile.get('is_administration', False),
                        'est_admin': profile.get('is_admin', False),
                        'est_actif': True
                    })()
                else:
                    del request.session['utilisateur_id']
                    request.utilisateur = None
            except Exception as e:
                print(f"Erreur middleware auth: {e}")
                del request.session['utilisateur_id']
                request.utilisateur = None
        else:
            request.utilisateur = None

        response = self.get_response(request)
        return response

def login_requis(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.utilisateur:
            messages.error(request, "Vous devez être connecté pour accéder à cette page.")
            return redirect('connexion')
        return view_func(request, *args, **kwargs)
    return wrapper

def permission_requise(permission_type):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.utilisateur:
                messages.error(request, "Vous devez être connecté pour accéder à cette page.")
                return redirect('connexion')
            
            if permission_type == 'bibliothecaire' and not request.utilisateur.est_bibliothecaire:
                messages.error(request, "Vous devez être bibliothécaire pour accéder à cette page.")
                return redirect('accueil')
            
            if permission_type == 'personnel' and not request.utilisateur.est_personnel:
                messages.error(request, "Vous devez être personnel pour accéder à cette page.")
                return redirect('accueil')
            
            if permission_type == 'admin' and not request.utilisateur.est_admin:
                messages.error(request, "Vous devez être administrateur pour accéder à cette page.")
                return redirect('accueil')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
