from django.db import models
from django.contrib.auth.models import User, AbstractUser, Group, Permission
from django.conf import settings


class Usager(AbstractUser):
    is_internal = models.BooleanField(default=False)
    is_external = models.BooleanField(default=False)
    is_company_member = models.BooleanField(default=False)

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
    ('membre_entreprise', 'Membre d\'entreprise'),
]

class ProfilBibliotheque(models.Model):
    utilisateur = models.ForeignKey('comptes.Usager', on_delete=models.CASCADE)
    type_utilisateur = models.CharField(
        max_length=20,
        choices=TYPE_UTILISATEUR_CHOICES,
        default='professionnel'  # ✅ ajoute une valeur par défaut ici
    )
    profession = models.CharField(max_length=100, blank=True, null=True)
    institution = models.CharField(max_length=100, blank=True, null=True)  # ✅ null=True ajouté
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

    utilisateur = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)


    # Infos personnelles
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20)
    email = models.EmailField()
    type_utilisateur = models.CharField(max_length=50, choices=TYPE_UTILISATEUR_CHOICES)

    # Infos sur l'ouvrage demandé
    categorie_ouvrage = models.CharField(max_length=200)
    titre_ouvrage = models.CharField(max_length=200)
    auteur_ouvrage = models.CharField(max_length=200, blank=True, null=True)
    numero_inventaire = models.CharField(max_length=100, blank=True, null=True)
    ancien_code = models.CharField(max_length=100, blank=True, null=True)

    # Autres détails
    raison = models.TextField()
    date_souhaitee = models.DateField()
    message = models.TextField(blank=True, null=True)

    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"RDV de {self.nom} {self.prenom} - {self.titre_ouvrage}"