from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import Usager, ProfilBibliotheque
from django.forms import Textarea
from .models import RendezVous


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
    class Meta:
        model = RendezVous
        fields = [
            'nom', 'prenom', 'telephone', 'email', 'type_utilisateur',
            'categorie_ouvrage', 'titre_ouvrage', 'auteur_ouvrage',
            'numero_inventaire', 'ancien_code', 'raison', 'date_souhaitee', 'message'
        ]
        widgets = {
            'date_souhaitee': forms.DateInput(attrs={'type': 'date'}),
            'raison': forms.Textarea(attrs={'rows': 2}),
            'message': forms.Textarea(attrs={'rows': 3}),
        }

