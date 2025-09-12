# bibliotheque/forms.py
from django import forms

class CategorieForm(forms.Form):
    nom = forms.CharField(
        label="Nom de la catégorie",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    image = forms.ImageField(
        label="Image de la catégorie",
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )

class LivreForm(forms.Form):
    titre = forms.CharField(
        label="Titre du livre",
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Titre du livre'})
    )
    auteur_texte = forms.CharField(
        label="Auteur",
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de l\'auteur'})
    )
    date_publication = forms.DateField(
        label="Date de publication",
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    image = forms.ImageField(
        label="Image du livre",
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'})
    )
    description = forms.CharField(
        label="Description",
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Résumé ou description'})
    )
    numero_inventaire = forms.CharField(
        label="Numéro d'inventaire",
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numéro d\'inventaire'})
    )
    ancien_code = forms.CharField(
        label="Ancien code",
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ancien code (si existant)'})
    )
    categorie_id = forms.CharField(
        label="Catégorie",
        widget=forms.HiddenInput()
    )