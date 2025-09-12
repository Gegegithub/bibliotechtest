from django.shortcuts import redirect
from django.urls import reverse
from functools import wraps
from django.contrib import messages
from django.http import HttpResponseForbidden

def login_requis(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('utilisateur_id'):
            messages.warning(request, "Veuillez vous connecter pour accéder à cette page.")
            return redirect(f"{reverse('connexion')}?next={request.path}")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def permission_requise(role):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.session.get('utilisateur_id'):
                messages.warning(request, "Veuillez vous connecter pour accéder à cette page.")
                return redirect(f"{reverse('connexion')}?next={request.path}")
            
            profile = request.session.get('utilisateur_profile', {})
            
            # Vérifier les permissions selon le rôle
            if role == 'admin' and not profile.get('is_admin'):
                return HttpResponseForbidden("Accès refusé : réservé aux administrateurs.")
            elif role == 'bibliothecaire' and not profile.get('is_librarian'):
                return HttpResponseForbidden("Accès refusé : réservé aux bibliothécaires.")
            elif role == 'personnel' and not profile.get('is_administration'):
                return HttpResponseForbidden("Accès refusé : réservé au personnel administratif.")
            
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

class AuthentificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Ajouter l'utilisateur à la requête si connecté
        request.utilisateur = None
        utilisateur_id = request.session.get('utilisateur_id')
        
        if utilisateur_id:
            # Ajouter les informations de l'utilisateur depuis la session
            request.utilisateur = type('Utilisateur', (), {
                'id': utilisateur_id,
                'email': request.session.get('utilisateur_email'),
                'profile': request.session.get('utilisateur_profile', {}),
                'is_authenticated': True
            })
            
            # Ajouter les rôles depuis le profil
            profile = request.session.get('utilisateur_profile', {})
            request.utilisateur.est_admin = profile.get('is_admin', False)
            request.utilisateur.est_bibliothecaire = profile.get('is_librarian', False)
            request.utilisateur.est_personnel = profile.get('is_administration', False)
        
        response = self.get_response(request)
        return response