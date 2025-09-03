# bibliotheque/forms.py
from django import forms
from .models import Categorie
from .models import Livre, Auteur

class CategorieForm(forms.ModelForm):
    class Meta:
        model = Categorie
        fields = ['nom', 'image']  # ajoute d'autres champs si nécessaire
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }

class LivreForm(forms.ModelForm):
    auteur_texte = forms.CharField(
        label="Auteur",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de l’auteur'})
    )

    class Meta:
        model = Livre
        # NE PAS mettre 'auteur' ici car on le gère via 'auteur_texte'
        fields = ['titre', 'auteur_texte', 'date_publication', 'image', 'description', 'numero_inventaire', 'ancien_code']
        widgets = {
            'titre': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre du livre'}),
            'date_publication': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Résumé ou description'}),
            'numero_inventaire': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numéro d’inventaire'}),
            'ancien_code': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ancien code (si existant)'}),
        }

    def save(self, commit=True):
        # Crée ou récupère l'auteur
        nom_auteur = self.cleaned_data.pop('auteur_texte')
        auteur, created = Auteur.objects.get_or_create(nom=nom_auteur)
        
        livre = super().save(commit=False)
        livre.auteur = auteur
        if commit:
            livre.save()
        return livre