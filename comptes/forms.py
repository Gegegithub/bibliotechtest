from django import forms
from django.forms import Textarea
from .models import Utilisateur, RendezVous
from bibliotheque.models import Livre


class InscriptionForm(forms.ModelForm):
    # Champs essentiels en premier
    prenom = forms.CharField(
        label="Prénom",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    nom = forms.CharField(
        label="Nom",
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    mot_de_passe = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    confirmer_mot_de_passe = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Utilisateur
        fields = [
            'prenom',
            'nom',
            'email',
            'mot_de_passe',
            'type_utilisateur',
            'profession',
            'institution',
            'secteur_activite',
            'adresse',
            'telephone',
            'photo'
        ]
        widgets = {
            'type_utilisateur': forms.Select(attrs={'class': 'form-control'}),
            'profession': forms.TextInput(attrs={'class': 'form-control'}),
            'institution': forms.TextInput(attrs={'class': 'form-control'}),
            'secteur_activite': forms.TextInput(attrs={'class': 'form-control'}),
            'adresse': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'style': 'max-width: 100%; resize: vertical;'
            }),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
        }
        help_texts = {
            'email': 'Cette adresse email sera utilisée pour vous connecter',
            'type_utilisateur': 'Sélectionnez le type qui correspond le mieux à votre profil',
            'profession': 'Votre profession actuelle',
            'institution': 'L\'établissement auquel vous êtes rattaché',
            'secteur_activite': 'Votre domaine d\'activité',
            'photo': 'Une photo de profil (optionnelle)'
        }

    def clean(self):
        cleaned_data = super().clean()
        mot_de_passe = cleaned_data.get("mot_de_passe")
        confirmer_mot_de_passe = cleaned_data.get("confirmer_mot_de_passe")
        email = cleaned_data.get("email")

        if mot_de_passe and confirmer_mot_de_passe:
            if mot_de_passe != confirmer_mot_de_passe:
                raise forms.ValidationError("Les mots de passe ne correspondent pas.")

        if email and Utilisateur.objects.filter(email=email).exists():
            raise forms.ValidationError("Un compte avec cet email existe déjà.")

        return cleaned_data

    def save(self, commit=True):
        utilisateur = super().save(commit=False)
        utilisateur.set_password(self.cleaned_data["mot_de_passe"])
        if commit:
            utilisateur.save()
        return utilisateur


class ConnexionForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    mot_de_passe = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )


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
            'date_souhaitee': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'raison': forms.Textarea(attrs={'rows': 2, 'class': 'form-control'}),
            'message': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'prenom': forms.TextInput(attrs={'class': 'form-control'}),
            'telephone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'type_utilisateur': forms.Select(attrs={'class': 'form-control'}),
            'ancien_code': forms.TextInput(attrs={'class': 'form-control'}),
            'numero_inventaire': forms.TextInput(attrs={'class': 'form-control'}),
        }

    def clean_livre_titre(self):
        titre = self.cleaned_data['livre_titre'].strip()
        try:
            livre_obj = Livre.objects.get(titre__iexact=titre)
        except Livre.DoesNotExist:
            raise forms.ValidationError(f"Aucun ouvrage trouvé avec le titre '{titre}'.")
        return livre_obj

    def clean(self):
        cleaned_data = super().clean()
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.livre = self.cleaned_data.get("livre_titre")  # objet Livre
        if commit:
            instance.save()
        return instance


class RendezVousUpdateForm(forms.ModelForm):
    class Meta:
        model = RendezVous
        fields = ['statut']
        widgets = {
            'statut': forms.Select(attrs={'class': 'form-control'})
        }