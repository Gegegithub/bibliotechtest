def roles(request):
    # Utiliser les données de session Supabase
    profile = request.session.get('utilisateur_profile', {})
    
    est_admin = profile.get('is_admin', False)
    est_bibliothecaire = profile.get('is_librarian', False)
    est_personnel = profile.get('is_administration', False)
    est_usager = not (est_admin or est_bibliothecaire or est_personnel)
    
    # Créer un objet utilisateur factice pour la compatibilité avec la navbar
    class UtilisateurFactice:
        def __init__(self, profile):
            self.is_admin = profile.get('is_admin', False)
            self.is_librarian = profile.get('is_librarian', False)
            self.is_administration = profile.get('is_administration', False)
            self.est_admin = profile.get('is_admin', False)
            self.est_bibliothecaire = profile.get('is_librarian', False)
            self.est_personnel = profile.get('is_administration', False)
            self.email = profile.get('email', '')
            self.nom = profile.get('nom', '')
            self.prenom = profile.get('prenom', '')
    
    # Créer l'objet utilisateur si un profil existe
    utilisateur = UtilisateurFactice(profile) if profile else None
    
    # Gestion des notifications (simplifiée pour l'instant)
    nb_notifications_biblio = 0
    nb_notifications_personnel = 0
    nb_notifications_usager = 0
    notifications_usager = []

    return {
        "utilisateur": utilisateur,
        "est_admin": est_admin,
        "est_bibliothecaire": est_bibliothecaire,
        "est_personnel": est_personnel,
        "est_usager": est_usager,
        "nb_notifications_biblio": nb_notifications_biblio,
        "nb_notifications_personnel": nb_notifications_personnel,
        "nb_notifications_usager": nb_notifications_usager,
        "notifications_usager": notifications_usager,
    }


