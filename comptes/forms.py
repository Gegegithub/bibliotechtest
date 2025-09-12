from django import forms

class InscriptionForm(forms.Form):
    email = forms.EmailField(label='Email')
    mot_de_passe = forms.CharField(label='Mot de passe', widget=forms.PasswordInput)
    confirmation_mot_de_passe = forms.CharField(label='Confirmer le mot de passe', widget=forms.PasswordInput)
    nom = forms.CharField(label='Nom')
    prenom = forms.CharField(label='Prénom')
    telephone = forms.CharField(label='Téléphone', required=False)
    adresse = forms.CharField(label='Adresse', required=False)
    institution = forms.CharField(label='Institution', required=False)
    secteur_activite = forms.CharField(label='Secteur d\'activité', required=False)
    type_utilisateur = forms.ChoiceField(
        label='Type d\'utilisateur',
        choices=[
            ('etudiant', 'Étudiant'),
            ('enseignant', 'Enseignant'),
            ('chercheur', 'Chercheur'),
            ('autre', 'Autre')
        ]
    )

    def clean(self):
        cleaned_data = super().clean()
        mot_de_passe = cleaned_data.get('mot_de_passe')
        confirmation = cleaned_data.get('confirmation_mot_de_passe')

        if mot_de_passe and confirmation and mot_de_passe != confirmation:
            raise forms.ValidationError('Les mots de passe ne correspondent pas.')

        return cleaned_data

class ConnexionForm(forms.Form):
    email = forms.EmailField(label='Email')
    mot_de_passe = forms.CharField(label='Mot de passe', widget=forms.PasswordInput)