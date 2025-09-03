from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usager, ProfilBibliotheque
from django.forms import Textarea
from .models import RendezVous
from bibliotheque.models import Livre


class Etape1InscriptionForm(UserCreationForm):
    class Meta:
        model = Usager
        fields = [
            'username',
            'first_name',
            'last_name',
            'email',
            'password1',
            'password2',
        ]

class Etape2ProfilForm(forms.ModelForm):
    class Meta:
        model = ProfilBibliotheque
        fields = ['profession', 'institution', 'adresse', 'secteur_activite', 'telephone', 'type_utilisateur', 'photo']
        widgets = {
            'adresse': Textarea(attrs={'rows': 3, 'style': 'max-width: 100%; resize: vertical;'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for fname, field in self.fields.items():
            if fname == 'photo':
                continue
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'

class RendezVousForm(forms.ModelForm):
    # Champ texte pour saisir le titre (lié à Livre)
    livre_titre = forms.CharField(
        label="Ouvrage",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )

    class Meta:
        model = RendezVous
        fields = [
            'nom', 'prenom', 'telephone', 'email', 'type_utilisateur',
            'livre_titre', 'ancien_code', 'numero_inventaire',
            'raison', 'date_souhaitee', 'message'
        ]
        widgets = {
            'date_souhaitee': forms.DateInput(attrs={'type': 'date'}),
            'raison': forms.Textarea(attrs={'rows': 2}),
            'message': forms.Textarea(attrs={'rows': 3}),
        }

    # Validation du titre : retourne l'objet Livre
    def clean_livre_titre(self):
        titre = self.cleaned_data['livre_titre'].strip()
        try:
            livre_obj = Livre.objects.get(titre__iexact=titre)
        except Livre.DoesNotExist:
            raise forms.ValidationError(f"Aucun ouvrage trouvé avec le titre '{titre}'.")
        return livre_obj

    # Validation globale : on ne bloque plus le formulaire pour les conflits
    def clean(self):
        cleaned_data = super().clean()
        # On ne fait plus de check de conflit ici
        # La vue s'occupera de gérer les conflits et d'afficher les livres alternatifs
        return cleaned_data

    # Sauvegarde : enregistre uniquement le lien vers le Livre
    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.livre = self.cleaned_data.get("livre_titre")  # objet Livre
        if commit:
            instance.save()
        return instance

    
class RendezVousUpdateForm(forms.ModelForm):
    class Meta:
        model = RendezVous
        fields = ['statut']  # On peut ajouter message si besoin
