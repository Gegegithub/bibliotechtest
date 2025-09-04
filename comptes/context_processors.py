def roles(request):
    utilisateur = request.utilisateur
    est_admin = False
    est_bibliothecaire = False
    est_personnel = False
    est_usager = False
    nb_notifications_biblio = 0
    nb_notifications_personnel = 0
    nb_notifications_usager = 0
    notifications_usager = []

    if utilisateur:
        est_admin = utilisateur.est_admin
        est_bibliothecaire = utilisateur.est_bibliothecaire
        est_personnel = utilisateur.est_personnel
        est_usager = not (est_admin or est_bibliothecaire or est_personnel)

        if hasattr(utilisateur, "notifications"):
            if est_bibliothecaire:
                nb_notifications_biblio = utilisateur.notifications.filter(lu=False).count()
            if est_personnel:
                nb_notifications_personnel = utilisateur.notifications.filter(lu=False).count()
            if est_usager:
                notifications_usager = utilisateur.notifications.filter(lu=False)
                nb_notifications_usager = notifications_usager.count()

    return {
        "est_admin": est_admin,
        "est_bibliothecaire": est_bibliothecaire,
        "est_personnel": est_personnel,
        "est_usager": est_usager,
        "nb_notifications_biblio": nb_notifications_biblio,
        "nb_notifications_personnel": nb_notifications_personnel,
        "nb_notifications_usager": nb_notifications_usager,
        "notifications_usager": notifications_usager,
    }


