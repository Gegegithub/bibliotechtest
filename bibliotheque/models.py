from django.db import models
from .utils import get_wikipedia_description 

class Auteur(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100, blank=True, null=True)

    class Meta:
        ordering = ['nom']

    def __str__(self):
        return f"{self.prenom or ''} {self.nom}".strip()

class Categorie(models.Model):
    nom = models.CharField(max_length=100)
    image = models.ImageField(upload_to='categorie_images/', null=True, blank=True)

    class Meta:
        ordering = ['nom']

    def __str__(self):
        return self.nom

    def nombre_livres(self):
        return self.livres.count()

   
class Livre(models.Model):
    titre = models.CharField(max_length=200)
    auteur = models.ForeignKey(Auteur, null=True, blank=True, on_delete=models.SET_NULL, related_name='livres')
    description = models.TextField(blank=True, null=True)  # biographie Wikipédia
    image = models.ImageField(upload_to='livres', null=True, blank=True)
    numero_inventaire = models.CharField(max_length=50, unique=True)
    ancien_code = models.CharField(max_length=50, blank=True, null=True)
    date_publication = models.DateField()
    categorie = models.ForeignKey(Categorie, on_delete=models.SET_NULL, null=True, related_name='livres')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Si description vide, on tente de la remplir depuis Wikipédia
        if not self.description and self.auteur:
            # On construit le nom complet de l'auteur
            author_name = f"{self.auteur.prenom or ''} {self.auteur.nom}".strip()
            wikipedia_bio = get_wikipedia_description(author_name)
            if wikipedia_bio:
                self.description = wikipedia_bio
        super().save(*args, **kwargs)

    def __str__(self):
        return self.titre
    
    


    
