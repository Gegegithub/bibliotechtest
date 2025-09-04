from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.utils import timezone
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseForbidden, JsonResponse, HttpResponse
from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Case, When, Value, IntegerField, Count, Avg, F, Q
from django.template.loader import render_to_string
from weasyprint import HTML
from datetime import date, timedelta
from .forms import InscriptionForm, ConnexionForm, RendezVousForm, RendezVousUpdateForm
from .models import Utilisateur, RendezVous, Notification
from bibliotheque.models import Livre
from .middleware import login_requis, permission_requise


def inscription(request):
    if request.method == "POST":
        form = InscriptionForm(request.POST, request.FILES)
        if form.is_valid():
            utilisateur = form.save()
            # Créer une session pour l'utilisateur
            request.session['utilisateur_id'] = utilisateur.id
            messages.success(request, "Inscription réussie ! Vous pouvez maintenant vous connecter.")
            return redirect('connexion')
        else:
            messages.error(request, "Veuillez corriger les erreurs du formulaire.")
    else:
        form = InscriptionForm()
    
    return render(request, 'inscription.html', {'form': form})


def connexion(request):
    if request.method == 'POST':
        form = ConnexionForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            mot_de_passe = form.cleaned_data['mot_de_passe']
            try:
                utilisateur = Utilisateur.objects.get(email=email)
                if utilisateur.check_password(mot_de_passe):
                    # Mettre à jour la dernière connexion
                    utilisateur.derniere_connexion = timezone.now()
                    utilisateur.save()
                    # Créer une session pour l'utilisateur
                    request.session['utilisateur_id'] = utilisateur.id
                    messages.success(request, "Vous êtes bien connecté(e) !")
                    
                    next_url = request.POST.get('next') or request.GET.get('next')
                    if next_url:
                        return redirect(next_url)
                    else:
                        return redirect('accueil')
                else:
                    messages.error(request, "Email ou mot de passe invalide.")
            except Utilisateur.DoesNotExist:
                messages.error(request, "Email ou mot de passe invalide.")
    else:
        form = ConnexionForm()

    next_url = request.GET.get('next', '')
    return render(request, 'connexion.html', {'form': form, 'next': next_url})


def Connexion(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next')
            return redirect(next_url if next_url else 'accueil')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")

    next_url = request.GET.get('next', '')
    return render(request, 'connexion.html', {'next': next_url})


def deconnexion(request):
    if 'utilisateur_id' in request.session:
        del request.session['utilisateur_id']
    messages.info(request, "Vous avez été déconnecté(e).")
    return redirect('accueil')





#Suivi des rendez-vous par l'utilisateur
@login_requis
def mes_rendezvous(request):
    # On récupère uniquement les rendez-vous de l'utilisateur connecté
    rdvs = RendezVous.objects.filter(utilisateur=request.utilisateur).order_by('-date_souhaitee')
    return render(request, 'mes_rendezvous.html', {'rdvs': rdvs})






    
@login_requis
def rendez_vous(request):
    livres_similaires = []
    message_indispo = None

    if request.method == "POST":
        form = RendezVousForm(request.POST)
        if form.is_valid():
            livre = form.cleaned_data['livre_titre']  # C'est déjà un objet Livre grâce au clean_livre_titre
            date = form.cleaned_data.get('date_souhaitee')

            conflit = RendezVous.objects.filter(
                livre=livre,
                date_souhaitee=date
            ).exclude(statut="annule").exists()

            if conflit:
                livres_similaires = Livre.objects.filter(categorie=livre.categorie).exclude(id=livre.id)
                message_indispo = f"L'ouvrage '{livre.titre}' n'est pas disponible à la date du {date}."
                return render(request, "rendez_vous.html", {
                    "form": form,
                    "livres_similaires": livres_similaires,
                    "message_indispo": message_indispo
                })

            # Sauvegarde si pas de conflit
            instance = form.save(commit=False)
            instance.utilisateur = request.utilisateur

            if not instance.statut:
                instance.statut = "en_attente"  # statut par défaut

            instance.save()

            # ✅ Créer notification pour le personnel administratif
            personnel = Utilisateur.objects.filter(est_personnel=True)
            for membre in personnel:
                Notification.objects.create(
                    utilisateur=membre,
                    message=f"Nouvelle demande de rendez-vous de {request.utilisateur.prenom} {request.utilisateur.nom}."
                )

            return redirect("confirmation_rdv")
    else:
        form = RendezVousForm()

    return render(request, "rendez_vous.html", {
        "form": form,
        "livres_similaires": livres_similaires,
        "message_indispo": message_indispo
    })




@login_requis
@permission_requise('personnel')
def gestion_rendezvous(request):
    # Récupérer tous les rendez-vous, triés par date
    rdvs = RendezVous.objects.all().order_by('date_souhaitee')

    # Initialiser les groupes par statut
    groupes = {
        'En attente': [],
        'Confirmés': [],
        'Terminés': [],
        'Annulés': [],
    }

    # Parcourir tous les rdvs et les ajouter dans le groupe correspondant
    for rdv in rdvs:
        statut = rdv.statut.lower()
        if statut == 'en_attente':
            groupes['En attente'].append(rdv)
        elif statut == 'confirme':
            groupes['Confirmés'].append(rdv)
        elif statut == 'termine':
            groupes['Terminés'].append(rdv)
        elif statut == 'annule':
            groupes['Annulés'].append(rdv)

    # Passer les groupes au template
    context = {
        'groupes': groupes
    }

    return render(request, 'gestion_rendezvous.html', context)





@login_requis
def modifier_rdv(request, id):
    # Vérifier que l'utilisateur est Personnel ou Admin
    if not (request.utilisateur.est_personnel):
        messages.error(request, "Vous devez être Personnel")
        return redirect('accueil')
    rdv = get_object_or_404(RendezVous, id=id)

    if request.method == "POST":
        # 1️⃣ Récupérer le statut et la date du formulaire
        nouveau_statut = request.POST.get("statut")
        date_souhaitee = request.POST.get("date_souhaitee")

        if date_souhaitee:
            rdv.date_souhaitee = date_souhaitee

        # 2️⃣ Vérifier le statut précédent
        statut_precedent = rdv.statut
        rdv.statut = nouveau_statut
        rdv.save()
        
        # 🔹 Déterminer le titre et l’auteur à afficher
        if rdv.livre:
            titre_ouvrage = rdv.livre.titre
            auteur_ouvrage = rdv.livre.auteur
        else:
            titre_ouvrage = rdv.titre_ouvrage or "non spécifié"
            auteur_ouvrage = getattr(rdv, "auteur_ouvrage", "non spécifié")

        # ✅ 3️⃣ Créer une notification pour l'UTILISATEUR concerné
        Notification.objects.create(
            utilisateur=rdv.utilisateur,
            message=(
                f"Le statut de votre rendez-vous du {rdv.date_souhaitee} "
                f"pour l'ouvrage « {titre_ouvrage} » "
                f"de l'auteur « {auteur_ouvrage} » est passé à : {rdv.get_statut_display()}"
            ),
            url=reverse("mes_rendezvous")
        )

        # 4️⃣ Créer une notification pour les bibliothécaires si le RDV est confirmé
        if statut_precedent == "en_attente" and nouveau_statut.lower() in ["confirme", "confirmé"]:
            bibliothecaires = Utilisateur.objects.filter(est_bibliothecaire=True)
            for biblio in bibliothecaires:
                Notification.objects.create(
                    utilisateur=biblio,
                    message=f"Nouveau rendez-vous confirmé pour {rdv.utilisateur.prenom} {rdv.utilisateur.nom}",
                    url=reverse('gestion_rdv_bibliothecaire')
                )

        # 5️⃣ Rediriger vers la gestion des rendez-vous
        return redirect('gestion_rendezvous')

    # 6️⃣ GET : afficher le formulaire de modification
    return render(request, "modifier_rdv.html", {"rdv": rdv})







@login_requis
@permission_requise('bibliothecaire')
def gestion_rdv_bibliothecaire(request):
    from datetime import datetime  # ✅ Import placé dans la vue comme tu l’as demandé

    today = timezone.now().date()

    # Tous les RDV confirmés
    rdvs_confirme = RendezVous.objects.filter(statut="confirme").order_by('date_souhaitee', 'heure_entree')

    # Séparer par jour
    rdvs_today = rdvs_confirme.filter(date_souhaitee=today)
    rdvs_future = rdvs_confirme.filter(date_souhaitee__gt=today)

    # Vérifier si on a reçu l'id d'une notification à marquer comme lue
    notif_id = request.GET.get('notif_id')
    if notif_id:
        try:
            notif = Notification.objects.get(id=notif_id, utilisateur=request.utilisateur)
            notif.lu = True
            notif.save()
        except Notification.DoesNotExist:
            pass

    if request.method == "POST":
        rdv_id = request.POST.get("rdv_id")
        rdv = get_object_or_404(RendezVous, id=rdv_id)

        heure_entree = request.POST.get("heure_entree")
        heure_sortie = request.POST.get("heure_sortie")

        # ✅ Convertir les chaînes HH:MM en objet time si non vide
        rdv.heure_entree = datetime.strptime(heure_entree, "%H:%M").time() if heure_entree else None
        rdv.heure_sortie = datetime.strptime(heure_sortie, "%H:%M").time() if heure_sortie else None

        rdv.save()
        return redirect("gestion_rdv_bibliothecaire")

    return render(request, "gestion_rdv_bibliothecaire.html", {
        "rdvs_today": rdvs_today,
        "rdvs_future": rdvs_future,
    })


def enregistrer_rdv(request):
    if request.method == "POST":
        rdv_id = request.POST.get("rdv_id")
        rdv = get_object_or_404(RendezVous, id=rdv_id)

        heure_entree = request.POST.get("heure_entree")
        heure_sortie = request.POST.get("heure_sortie")

        from datetime import datetime
        rdv.heure_entree = datetime.strptime(heure_entree, "%H:%M").time() if heure_entree else None
        rdv.heure_sortie = datetime.strptime(heure_sortie, "%H:%M").time() if heure_sortie else None
        rdv.save()

        return JsonResponse({"status": "ok"})







# ===================== NOUVELLE VUE CONFIRMER RDV =====================


@login_requis
@permission_requise('admin')
def confirmer_rendezvous(request, rendezvous_id):
    rdv = get_object_or_404(RendezVous, id=rendezvous_id)

    if request.method == "POST":
        rdv.statut = "confirmé"
        rdv.save()

        # Notification pour tous les bibliothécaires
        # Notifier les bibliothécaires
        bibliothecaires = Utilisateur.objects.filter(est_bibliothecaire=True)
        for biblio in bibliothecaires:
            Notification.objects.create(
                utilisateur=biblio,
                message="Nouveau rendez-vous ajouté, vous pouvez consulter la liste des rendez-vous.",
                url=reverse('gestion_rendezvous')  # lien vers la page de gestion
            )

        messages.success(request, "Le rendez-vous a été confirmé et les bibliothécaires ont été notifiés.")
        return redirect("gestion_rendezvous")

    return render(request, "confirmer_rendezvous.html", {"rdv": rdv})

# ===================================================================


@login_requis
def notifications(request):
    # Vérifie le groupe
    if not request.utilisateur.est_bibliothecaire:
        return HttpResponseForbidden("Vous n'êtes pas autorisé à accéder à cette page.")

    notifs = request.utilisateur.notifications.filter(lu=False).order_by('-created_at')
    
    return render(request, "notifications.html", {"notifications": notifs})

@login_requis
def notifications_usager(request):
    notifs = request.utilisateur.notifications.all().order_by('-created_at')
    nb_notifications_non_lues = request.utilisateur.notifications.filter(lu=False).count()
    toutes_lues = all(notif.lu for notif in notifs)
    
    return render(request, "mes_notifications.html", {
        "notifications": notifs,
        "toutes_lues": toutes_lues,
        "notifications_unread_count": nb_notifications_non_lues,
        "est_usager": True,  # ou selon ton système de groupes
    })




@login_requis
def notifier_rdv(request, rdv_id):
    rdv = get_object_or_404(RendezVous, id=rdv_id)

    if request.method == "POST":
        # 🔹 Récupérer le titre du livre : priorité au lien ForeignKey, sinon fallback sur titre_ouvrage
        if rdv.livre:
            titre_ouvrage = rdv.livre.titre
            auteur_ouvrage = rdv.livre.auteur  # si tu veux aussi l'auteur
        else:
            titre_ouvrage = rdv.titre_ouvrage or "non spécifié"
            auteur_ouvrage = rdv.auteur_ouvrage or "non spécifié"

        # 1️⃣ Envoi du mail à l'utilisateur
        send_mail(
            subject="Votre rendez-vous a été confirmé",
            message=(
                f"Bonjour {rdv.utilisateur.first_name},\n\n"
                f"Le statut de votre rendez-vous du {rdv.date_souhaitee} "
                f"pour l'ouvrage \"{titre_ouvrage}\" a été confirmé.\n\n"
                f"Auteur : {auteur_ouvrage}"
            ),
            from_email="admin@bibliotech.com",
            recipient_list=[rdv.utilisateur.email],
        )

        # 2️⃣ Création de notification pour l'utilisateur
        Notification.objects.create(
            utilisateur=rdv.utilisateur,
            message=f"Le statut de votre rendez-vous du {rdv.date_souhaitee} "
                    f"pour l'ouvrage \"{titre_ouvrage}\" est passé à : {rdv.statut}"
        )

        # 3️⃣ Création de notifications pour les bibliothécaires
        bibliothecaires = Utilisateur.objects.filter(est_bibliothecaire=True)
        for biblio in bibliothecaires:
            Notification.objects.create(
                utilisateur=biblio,
                message=f"Nouveau rendez-vous confirmé avec {rdv.utilisateur.first_name} {rdv.utilisateur.last_name}"
            )

        messages.success(request, "L'utilisateur a été notifié et les bibliothécaires ont reçu une notification.")
        return redirect('gestion_rendezvous')

    messages.warning(request, "La notification n'a pas pu être envoyée.")
    return redirect('gestion_rendezvous')



@login_requis
@permission_requise('admin')
def notifications_personnel(request):
    notifications = request.utilisateur.notifications.filter(lu=False).order_by("-created_at")
    return render(request, "notifications/liste.html", {"notifications": notifications})

def notifications_counts(request):
    nb_notifications_personnel = 0
    nb_notifications_usager = 0

    if request.utilisateur.is_authenticated:
        # Notifications pour le personnel administratif
        if request.utilisateur.est_personnel:
            nb_notifications_personnel = request.utilisateur.notifications.filter(lu=False).count()

        # Notifications pour l'usager
        elif not (request.utilisateur.est_bibliothecaire or request.utilisateur.est_personnel):
            nb_notifications_usager = request.utilisateur.notifications.filter(lu=False).count()

    return {
        "nb_notifications_personnel": nb_notifications_personnel,
        "nb_notifications_usager": nb_notifications_usager
    }







@login_requis
def creer_rdv(request):
    if request.method == "POST":
        # Récupérer les données du formulaire
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        email = request.POST.get('email')
        date_souhaitee = request.POST.get('date_souhaitee')
        titre_ouvrage = request.POST.get('titre_ouvrage', '')

        # Créer le rendez-vous
        rdv = RendezVous.objects.create(
            nom=nom,
            prenom=prenom,
            email=email,
            date_souhaitee=date_souhaitee,
            statut="en_attente",
            titre_ouvrage=titre_ouvrage,
            utilisateur=request.utilisateur
        )

        # Notifier les membres du personnel administratif
        # Notifier le personnel administratif
        personnel = Utilisateur.objects.filter(est_personnel=True)
        for membre in personnel:
            Notification.objects.create(
                utilisateur=membre,
                message=f"Nouvelle demande de rendez-vous de {rdv.nom} {rdv.prenom}."
            )

        # Redirection vers la confirmation
        return redirect('confirmation_rdv')

    # Si GET ou autre méthode, rediriger vers la page de rendez-vous
    return redirect('rendez_vous')

@login_requis
def lire_notification(request, notification_id):
    # Récupérer la notification pour l'utilisateur connecté
    notif = get_object_or_404(Notification, id=notification_id, utilisateur=request.utilisateur)
    
    # Marquer comme lue
    notif.lu = True
    notif.save()
    
    # Redirection selon le type d'utilisateur
    if request.utilisateur.est_personnel:
        # Pour le personnel admin, respecter l'URL si elle existe
        return redirect(notif.url if notif.url else 'gestion_rendezvous')
    elif not (request.utilisateur.est_bibliothecaire or request.utilisateur.est_personnel):
        # Pour les usagers, rediriger toujours vers mes_rendezvous
        return redirect('mes_rendezvous')
    else:
        # Pour les bibliothécaires ou autres, fallback
        return redirect('accueil')



@login_requis
def notification_marquer_lue(request, notif_id):
    # Récupère la notification pour l'utilisateur connecté
    notif = get_object_or_404(Notification, id=notif_id, utilisateur=request.utilisateur)
    
    # Marquer comme lue
    notif.lu = True
    notif.save()
    
    # Redirection selon le groupe de l'utilisateur
    if request.utilisateur.est_personnel:
        return redirect('gestion_rendezvous')  # page admin
    elif request.utilisateur.est_bibliothecaire:
        return redirect('gestion_rdv_bibliothecaire')  # page bibliothécaire
    else:
        # Pour les usagers, rediriger vers mes_rendezvous
        return redirect('mes_rendezvous')




@login_requis
def home(request):
    # Vérifie si l'utilisateur est bibliothécaire
    est_biblio = request.utilisateur.groups.filter(name="Bibliothécaire").exists()

    # Compteur de notifications non lues pour **tous les utilisateurs**
    nb_notifications = request.utilisateur.notifications.filter(lu=False).count()

    return render(request, "index.html", {
        "est_bibliothecaire": est_biblio,
        "nb_notifications": nb_notifications,
    })




def accueil(request):
    return render(request, 'accueil.html')


@login_requis
def mon_compte(request):
    return render(request, 'mon_compte.html')



def modifier_informations(request):
    return render(request, 'modifier_informations.html')


def changer_mot_de_passe(request):
    return render(request, 'changer_mot_de_passe.html')


def support_contact(request):
    return render(request, 'support_contact.html')


def conditions_generales(request):
    return render(request, 'conditions_generales.html')

def confirmation_rdv(request):
    return render(request, 'confirmation_rdv.html')


@login_requis
def tableau_de_bord(request):
    # 🔒 Restriction d'accès : superuser, bibliothécaire ou personnel administratif
    if not (request.utilisateur.est_admin or
            request.utilisateur.est_bibliothecaire or
            request.utilisateur.est_personnel):
        return HttpResponseForbidden("Accès refusé : réservé au personnel autorisé.")

    today = date.today()
    last_week = today - timedelta(days=7)

    # -------------------
    # 1️⃣ Usagers actifs
    # -------------------
    total_usagers_actifs = Utilisateur.objects.filter(
        rendezvous__isnull=False
    ).distinct().count()

    # -------------------
    # 2️⃣ Nombre de livres empruntés par jour (7 derniers jours)
    # -------------------
    flux_journalier = (
        RendezVous.objects.filter(date_souhaitee__gte=last_week)
        .values('date_souhaitee')
        .annotate(count=Count('id'))
        .order_by('date_souhaitee')
    )

    # -------------------
    # 3️⃣ Temps moyen d'emprunt / rendez-vous
    # -------------------
    rdvs_today = RendezVous.objects.filter(date_souhaitee=today)
    avg_duree = (
        sum(
            (rdv.heure_sortie - rdv.heure_entree).total_seconds() / 60
            for rdv in rdvs_today
            if rdv.heure_sortie and rdv.heure_entree
        ) / max(rdvs_today.count(), 1)
    )

    # -------------------
    # 4️⃣ Livres les plus populaires
    # -------------------
    top_livres = (
        RendezVous.objects.values('livre__titre')
        .annotate(nb_emprunts=Count('id'))
        .order_by('-nb_emprunts')[:5]
    )

    # -------------------
    # 5️⃣ Livres peu empruntés
    # -------------------
    seuil_peu_emprunte = 2
    livres_peu_empruntes = (
        Livre.objects.annotate(nb_rdv=Count('rendezvous'))
        .filter(nb_rdv__lte=seuil_peu_emprunte)
    )

    # -------------------
    # 6️⃣ Taux d'occupation par catégorie
    # -------------------
    rdv_par_categorie = (
        RendezVous.objects.values('livre__categorie__nom')
        .annotate(count=Count('id'))
    )
    total_rdv = RendezVous.objects.count()
    taux_occupation_categorie = [
        {
            'categorie': c['livre__categorie__nom'],
            'pourcentage': round((c['count'] / max(total_rdv, 1)) * 100, 1)
        }
        for c in rdv_par_categorie
    ]

    # -------------------
    # 7️⃣ Rendez-vous annulés ou manqués
    # -------------------
    rdv_non_honores = RendezVous.objects.filter(
        Q(statut='annule') | Q(statut='termine')
    ).count()

    # -------------------
    # 8️⃣ Nombre d'usagers par type
    # -------------------
    usagers_par_type = (
        Utilisateur.objects.values('type_utilisateur')
        .annotate(count=Count('id'))
    )

    # -------------------
    # 9️⃣ Flux de visiteurs par jour/semaine
    # -------------------
    flux_semaine = (
        RendezVous.objects.filter(date_souhaitee__gte=last_week)
        .extra({'day': "date(date_souhaitee)"})
        .values('day')
        .annotate(count=Count('id'))
        .order_by('day')
    )

    context = {
        'total_usagers_actifs': total_usagers_actifs,
        'flux_journalier': flux_journalier,
        'avg_duree': round(avg_duree, 1),
        'top_livres': top_livres,
        'livres_peu_empruntes': livres_peu_empruntes,
        'taux_occupation_categorie': taux_occupation_categorie,
        'rdv_non_honores': rdv_non_honores,
        'usagers_par_type': usagers_par_type,
        'flux_semaine': flux_semaine,
    }

    return render(request, "dashboard.html", context)


@login_requis
def administration_utilisateurs(request):
    """
    Vue d'administration des utilisateurs - accessible uniquement au premier utilisateur (super admin)
    """
    # Vérifier si l'utilisateur est le premier utilisateur (super admin)
    premier_utilisateur = Utilisateur.objects.order_by('date_inscription').first()
    
    if not premier_utilisateur or request.utilisateur.id != premier_utilisateur.id:
        messages.error(request, "Accès refusé : cette fonctionnalité est réservée au super administrateur.")
        return redirect('accueil')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        utilisateur_id = request.POST.get('utilisateur_id')
        
        try:
            utilisateur_cible = Utilisateur.objects.get(id=utilisateur_id)
            
            if action == 'promouvoir_lecteur':
                # Lecteur = utilisateur simple (aucun rôle spécial)
                utilisateur_cible.est_admin = False
                utilisateur_cible.est_bibliothecaire = False
                utilisateur_cible.est_personnel = False
                messages.success(request, f"{utilisateur_cible.prenom} {utilisateur_cible.nom} a été promu lecteur.")
                
            elif action == 'promouvoir_bibliothecaire':
                # Bibliothécaire = gestion des livres et RDV
                utilisateur_cible.est_bibliothecaire = True
                utilisateur_cible.est_admin = False
                utilisateur_cible.est_personnel = False
                messages.success(request, f"{utilisateur_cible.prenom} {utilisateur_cible.nom} a été promu bibliothécaire.")
                
            elif action == 'promouvoir_personnel':
                # Personnel = gestion administrative et RDV
                utilisateur_cible.est_personnel = True
                utilisateur_cible.est_admin = False
                utilisateur_cible.est_bibliothecaire = False
                messages.success(request, f"{utilisateur_cible.prenom} {utilisateur_cible.nom} a été promu personnel administratif.")
                
            elif action == 'activer_compte':
                utilisateur_cible.est_actif = True
                messages.success(request, f"Le compte de {utilisateur_cible.prenom} {utilisateur_cible.nom} a été activé.")
                
            elif action == 'desactiver_compte':
                utilisateur_cible.est_actif = False
                messages.success(request, f"Le compte de {utilisateur_cible.prenom} {utilisateur_cible.nom} a été désactivé.")
            
            utilisateur_cible.save()
            
        except Utilisateur.DoesNotExist:
            messages.error(request, "Utilisateur introuvable.")
        except Exception as e:
            messages.error(request, f"Erreur lors de la modification : {str(e)}")
    
    # Récupérer tous les utilisateurs sauf le super admin
    utilisateurs = Utilisateur.objects.exclude(id=premier_utilisateur.id).order_by('-date_inscription')
    
    # Calculer les statistiques (sans le super admin)
    total_utilisateurs = Utilisateur.objects.exclude(id=premier_utilisateur.id).count()
    nb_lecteurs = Utilisateur.objects.filter(
        est_admin=False, 
        est_bibliothecaire=False, 
        est_personnel=False
    ).exclude(id=premier_utilisateur.id).count()
    nb_bibliothecaires = Utilisateur.objects.filter(est_bibliothecaire=True).exclude(id=premier_utilisateur.id).count()
    nb_personnel = Utilisateur.objects.filter(est_personnel=True).exclude(id=premier_utilisateur.id).count()
    
    context = {
        'utilisateurs': utilisateurs,
        'premier_utilisateur': premier_utilisateur,
        'total_utilisateurs': total_utilisateurs,
        'nb_lecteurs': nb_lecteurs,
        'nb_bibliothecaires': nb_bibliothecaires,
        'nb_personnel': nb_personnel,
    }
    
    return render(request, 'administration_utilisateurs.html', context)


def generer_rapport_pdf(request):
    today = date.today()
    last_week = today - timedelta(days=7)

    # Données du dashboard
    total_usagers_actifs = Utilisateur.objects.filter(rendezvous__isnull=False).distinct().count()
    flux_journalier = RendezVous.objects.filter(date_souhaitee=today)
    top_livres = (
        RendezVous.objects.values('livre__titre')
        .annotate(nb_emprunts=Count('id'))
        .order_by('-nb_emprunts')[:5]
    )
    usagers_par_type = (
        Utilisateur.objects.values('profilutilisateur__type_utilisateur')
        .annotate(count=Count('id'))
    )

    context = {
        'total_usagers_actifs': total_usagers_actifs,
        'flux_journalier': flux_journalier,
        'top_livres': top_livres,
        'usagers_par_type': usagers_par_type,
    }

    # Génération du HTML
    html_string = render_to_string('rapport.html', context)

    # Création du PDF
    pdf = HTML(string=html_string).write_pdf()

    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'inline; filename="rapport_dashboard.pdf"'
    return response









