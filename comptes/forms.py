from django import forms
from django.forms import Textarea


class InscriptionForm(forms.Form):
    # Champs essentiels en premier
    prenom = forms.CharField(
        label="Prénom",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    nom = forms.CharField(
        label="Nom",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
        help_text='Cette adresse email sera utilisée pour vous connecter'
    )
    mot_de_passe = forms.CharField(
        label="Mot de passe",
        min_length=6,
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    confirmer_mot_de_passe = forms.CharField(
        label="Confirmer le mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )
    
    # Champs optionnels
    type_utilisateur = forms.ChoiceField(
        label="Type d'utilisateur",
        choices=[
            ('etudiant', 'Étudiant'),
            ('professionnel', 'Professionnel'),
            ('membre_entreprise', "Membre d'entreprise")
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text='Sélectionnez le type qui correspond le mieux à votre profil'
    )
    profession = forms.CharField(
        label="Profession",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text='Votre profession actuelle'
    )
    institution = forms.CharField(
        label="Institution",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="L'établissement auquel vous êtes rattaché"
    )
    secteur_activite = forms.CharField(
        label="Secteur d'activité",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        help_text="Votre domaine d'activité"
    )
    adresse = forms.CharField(
        label="Adresse",
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'style': 'max-width: 100%; resize: vertical;'
        })
    )
    telephone = forms.CharField(
        label="Téléphone",
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )

    def clean(self):
        cleaned_data = super().clean()
        mot_de_passe = cleaned_data.get("mot_de_passe")
        confirmer_mot_de_passe = cleaned_data.get("confirmer_mot_de_passe")

        if mot_de_passe and confirmer_mot_de_passe:
            if mot_de_passe != confirmer_mot_de_passe:
                raise forms.ValidationError("Les mots de passe ne correspondent pas.")

        return cleaned_data


class ConnexionForm(forms.Form):
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    mot_de_passe = forms.CharField(
        label="Mot de passe",
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )


class RendezVousForm(forms.Form):
    # Informations personnelles
    nom = forms.CharField(
        label="Nom",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    prenom = forms.CharField(
        label="Prénom",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    telephone = forms.CharField(
        label="Téléphone",
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    type_utilisateur = forms.ChoiceField(
        label="Type d'utilisateur",
        choices=[
            ('etudiant_chercheur', 'Étudiant Chercheur'),
            ('professeur_chercheur', 'Professeur Chercheur'),
            ('academique', 'Académique'),
            ('professionnel', 'Professionnel'),
            ('porteur_projet', 'Porteur de projet'),
            ('autre', 'Autre'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    # Informations sur le livre
    livre_titre = forms.CharField(
        label="Ouvrage",
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    ancien_code = forms.CharField(
        label="Ancien code",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    numero_inventaire = forms.CharField(
        label="Numéro d'inventaire",
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    # Détails du rendez-vous
    raison = forms.CharField(
        label="Raison de la demande",
        widget=forms.Textarea(attrs={'rows': 2, 'class': 'form-control'})
    )
    date_souhaitee = forms.DateField(
        label="Date souhaitée",
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    message = forms.CharField(
        label="Message",
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})
    )


class RendezVousUpdateForm(forms.Form):
    statut = forms.ChoiceField(
        label="Statut",
        choices=[
            ('en_attente', 'En attente'),
            ('confirme', 'Confirmé'),
            ('annule', 'Annulé'),
            ('termine', 'Terminé'),
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )