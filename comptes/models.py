from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone
from bibliotheque.models import Livre


class Utilisateur(models.Model):
    # Informations d'authentification
    email = models.EmailField(
        unique=True,
        verbose_name="Email",
        help_text="Cette adresse email sera utilisée pour vous connecter"
    )
    mot_de_passe = models.CharField(
        max_length=128,
        verbose_name="Mot de passe"
    )
    
    # Informations personnelles
    prenom = models.CharField(
        max_length=100,
        verbose_name="Prénom"
    )
    nom = models.CharField(
        max_length=100,
        verbose_name="Nom"
    )
    type_utilisateur = models.CharField(
        max_length=20,
        choices=[
            ('etudiant', 'Étudiant'),
            ('professionnel', 'Professionnel'),
            ('membre_entreprise', "Membre d'entreprise")
        ],
        verbose_name="Type d'utilisateur",
        help_text="Sélectionnez le type qui correspond le mieux à votre profil"
    )
    profession = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Profession",
        help_text="Votre profession actuelle"
    )
    institution = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Institution",
        help_text="L'établissement auquel vous êtes rattaché"
    )
    secteur_activite = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Secteur d'activité",
        help_text="Votre domaine d'activité"
    )
    adresse = models.TextField(
        blank=True,
        null=True,
        verbose_name="Adresse"
    )
    telephone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name="Téléphone"
    )
    photo = models.ImageField(
        upload_to='photos_usagers/',
        blank=True,
        null=True,
        verbose_name="Photo de profil",
        help_text="Une photo de profil (optionnelle)"
    )
    
    # Dates
    date_inscription = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date d'inscription"
    )
    derniere_connexion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Dernière connexion"
    )
    
    # Rôles et statuts
    est_actif = models.BooleanField(
        default=True,
        verbose_name="Compte actif"
    )
    est_admin = models.BooleanField(
        default=False,
        verbose_name="Administrateur"
    )
    est_bibliothecaire = models.BooleanField(
        default=False,
        verbose_name="Bibliothécaire"
    )
    est_personnel = models.BooleanField(
        default=False,
        verbose_name="Personnel"
    )
    
    # Relations
    favoris = models.ManyToManyField(
        'bibliotheque.Livre',
        blank=True,
        related_name="favoris_utilisateurs",
        verbose_name="Livres favoris"
    )

    class Meta:
        verbose_name = "Utilisateur"
        verbose_name_plural = "Utilisateurs"
        ordering = ['-date_inscription']

    def set_password(self, raw_password):
        self.mot_de_passe = make_password(raw_password)

    def check_password(self, raw_password):
        return check_password(raw_password, self.mot_de_passe)

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.email})"
    
    def save(self, *args, **kwargs):
        # Si c'est le premier utilisateur, le rendre super admin
        if not Utilisateur.objects.exists():
            self.est_admin = True
            self.est_actif = True
        super().save(*args, **kwargs)


class RendezVous(models.Model):
    TYPE_UTILISATEUR_CHOICES = [
        ('etudiant_chercheur', 'Étudiant Chercheur'),
        ('professeur_chercheur', 'Professeur Chercheur'),
        ('academique', 'Académique'),
        ('professionnel', 'Professionnel'),
        ('porteur_projet', 'Porteur de projet'),
        ('autre', 'Autre'),
    ]

    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('confirme', 'Confirmé'),
        ('annule', 'Annulé'),
        ('termine', 'Terminé'),
    ]

    utilisateur = models.ForeignKey(
        'Utilisateur', 
        on_delete=models.CASCADE,
        verbose_name="Utilisateur"
    )
    statut = models.CharField(
        max_length=20, 
        choices=STATUT_CHOICES, 
        default='en_attente',
        verbose_name="Statut"
    )

    # Infos personnelles
    nom = models.CharField(
        max_length=100,
        verbose_name="Nom"
    )
    prenom = models.CharField(
        max_length=100,
        verbose_name="Prénom"
    )
    telephone = models.CharField(
        max_length=20,
        verbose_name="Téléphone"
    )
    email = models.EmailField(
        verbose_name="Email"
    )
    type_utilisateur = models.CharField(
        max_length=50, 
        choices=TYPE_UTILISATEUR_CHOICES,
        verbose_name="Type d'utilisateur"
    )

    # Lien direct vers un livre
    livre = models.ForeignKey(
        'bibliotheque.Livre', 
        on_delete=models.CASCADE, 
        related_name="rendezvous",
        verbose_name="Livre"
    )

    # Champs redondants (optionnels, pour archivage)
    titre_ouvrage = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Titre de l'ouvrage"
    )
    auteur_ouvrage = models.CharField(
        max_length=200,
        blank=True,
        null=True,
        verbose_name="Auteur de l'ouvrage"
    )
    numero_inventaire = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Numéro d'inventaire"
    )
    ancien_code = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="Ancien code"
    )

    # Autres détails
    raison = models.TextField(
        verbose_name="Raison de la demande"
    )
    date_souhaitee = models.DateField(
        verbose_name="Date souhaitée"
    )
    message = models.TextField(
        blank=True,
        null=True,
        verbose_name="Message"
    )

    date_creation = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )

    # Pour le bibliothécaire
    heure_entree = models.TimeField(
        blank=True,
        null=True,
        verbose_name="Heure d'entrée"
    )
    heure_sortie = models.TimeField(
        blank=True,
        null=True,
        verbose_name="Heure de sortie"
    )

    class Meta:
        verbose_name = "Rendez-vous"
        verbose_name_plural = "Rendez-vous"
        ordering = ['-date_creation']

    def __str__(self):
        return f"RDV de {self.nom} {self.prenom} - {self.livre.titre} ({self.date_souhaitee})"


class Notification(models.Model):
    utilisateur = models.ForeignKey(
        'Utilisateur',
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="Utilisateur"
    )
    message = models.TextField(
        verbose_name="Message"
    )
    url = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="URL"
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Date de création"
    )
    lu = models.BooleanField(
        default=False,
        verbose_name="Lu"
    )

    class Meta:
        verbose_name = "Notification"
        verbose_name_plural = "Notifications"
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification pour {self.utilisateur.email}: {self.message[:30]}..."