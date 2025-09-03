def roles(request):
    user = request.user
    est_bibliothecaire = False
    est_personnel_admin = False
    est_usager = False
    nb_notifications_biblio = 0
    nb_notifications_personnel = 0
    nb_notifications_usager = 0
    notifications_usager = []

    if user.is_authenticated:
        est_bibliothecaire = user.groups.filter(name="Bibliothécaire").exists()
        est_personnel_admin = user.groups.filter(name="Personnel administratif").exists()
        est_usager = not (est_bibliothecaire or est_personnel_admin)

        if hasattr(user, "notifications"):
            if est_bibliothecaire:
                nb_notifications_biblio = user.notifications.filter(lu=False).count()
            if est_personnel_admin:
                nb_notifications_personnel = user.notifications.filter(lu=False).count()
            if est_usager:
                notifications_usager = user.notifications.filter(lu=False)
                nb_notifications_usager = notifications_usager.count()

    return {
        "est_bibliothecaire": est_bibliothecaire,
        "est_personnel_admin": est_personnel_admin,
        "est_usager": est_usager,
        "nb_notifications_biblio": nb_notifications_biblio,
        "nb_notifications_personnel": nb_notifications_personnel,
        "nb_notifications_usager": nb_notifications_usager,
        "notifications_usager": notifications_usager,
    }


