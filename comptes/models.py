from django.db import models 
from django.contrib.auth.models import User, AbstractUser, Group, Permission 
from django.conf import settings
from bibliotheque.models import Livre



class Usager(AbstractUser):
    is_internal = models.BooleanField(default=False)
    is_external = models.BooleanField(default=False)
    is_company_member = models.BooleanField(default=False)
    is_bibliothecaire = models.BooleanField(default=False)  # ✅ pour identifier le bibliothécaire


    groups = models.ManyToManyField(
        Group,
        related_name='usager_set',
        blank=True,
        help_text='Les groupes auxquels cet utilisateur appartient.',
        related_query_name='usager',
        verbose_name='groupes'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='usager_set',
        blank=True,
        help_text='Permissions spécifiques pour cet utilisateur.',
        related_query_name='usager',
        verbose_name='permissions utilisateur'
    )


TYPE_UTILISATEUR_CHOICES = [
    ('etudiant', 'Étudiant'),
    ('professionnel', 'Professionnel'),
    ('membre_entreprise', "Membre d'entreprise"),
]


class ProfilBibliotheque(models.Model):
    utilisateur = models.ForeignKey('comptes.Usager', on_delete=models.CASCADE)
    type_utilisateur = models.CharField(
        max_length=20,
        choices=TYPE_UTILISATEUR_CHOICES,
        default='professionnel'
    )
    profession = models.CharField(max_length=100, blank=True, null=True)
    institution = models.CharField(max_length=100, blank=True, null=True)
    secteur_activite = models.CharField(max_length=100, blank=True, null=True)
    adresse = models.TextField(blank=True, null=True)
    telephone = models.CharField(max_length=20, blank=True, null=True)
    photo = models.ImageField(upload_to='photos_usagers/', blank=True, null=True)
    favoris = models.ManyToManyField('bibliotheque.Livre', blank=True, related_name="favoris_utilisateurs")

    def __str__(self):
        return f"Profil de {self.utilisateur.username}"


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
        settings.AUTH_USER_MODEL, 
        on_delete=models.CASCADE
    )
    statut = models.CharField(
        max_length=20, 
        choices=STATUT_CHOICES, 
        default='en_attente'
    )

    # Infos personnelles
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20)
    email = models.EmailField()
    type_utilisateur = models.CharField(
        max_length=50, 
        choices=TYPE_UTILISATEUR_CHOICES
    )

    # 🔑 Lien direct vers un livre
    livre = models.ForeignKey(
        Livre, 
        on_delete=models.CASCADE, 
        related_name="rendezvous"
    )

    # Champs redondants (optionnels, pour archivage)
    
    titre_ouvrage = models.CharField(max_length=200, blank=True, null=True)
    auteur_ouvrage = models.CharField(max_length=200, blank=True, null=True)
    numero_inventaire = models.CharField(max_length=100, blank=True, null=True)
    ancien_code = models.CharField(max_length=100, blank=True, null=True)

    # Autres détails
    raison = models.TextField()
    date_souhaitee = models.DateField()
    message = models.TextField(blank=True, null=True)

    date_creation = models.DateTimeField(auto_now_add=True)

    # Pour le bibliothécaire
    heure_entree = models.TimeField(blank=True, null=True)
    heure_sortie = models.TimeField(blank=True, null=True)

    def __str__(self):
        return f"RDV de {self.nom} {self.prenom} - {self.livre.titre} ({self.date_souhaitee})"


class Notification(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    url = models.CharField(max_length=255, blank=True, null=True)  # Nouveau champ pour le lien
    created_at = models.DateTimeField(auto_now_add=True)
    lu = models.BooleanField(default=False)  # Pour savoir si la notif a été lue ou non

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Notification pour {self.user.username}: {self.message[:30]}..."


