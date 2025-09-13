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

class RendezVousForm(forms.Form):
    # Champs d'informations personnelles (en lecture seule)
    nom = forms.CharField(
        label='Nom',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': True,
            'style': 'background-color: #f8f9fa;'
        })
    )
    
    prenom = forms.CharField(
        label='Prénom',
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': True,
            'style': 'background-color: #f8f9fa;'
        })
    )
    
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'readonly': True,
            'style': 'background-color: #f8f9fa;'
        })
    )
    
    telephone = forms.CharField(
        label='Téléphone',
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'readonly': True,
            'style': 'background-color: #f8f9fa;',
            'placeholder': 'Entrez votre numéro'
        })
    )
    
    # Champs correspondant au code TypeScript
    profil = forms.ChoiceField(
        label='Profil',
        choices=[
            ('etudiant_chercheur', 'Étudiant/Chercheur'),
            ('professionnel', 'Professionnel'),
            ('entrepreneur', 'Entrepreneur'),
            ('membre_entreprise', 'Membre d\'entreprise')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    raison = forms.ChoiceField(
        label='Raison',
        choices=[
            ('formation', 'Formation'),
            ('recherche', 'Recherche'),
            ('preparation_diplome', 'Préparation diplôme')
        ],
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    appointment_date = forms.DateTimeField(
        label='Date du rendez-vous',
        widget=forms.DateTimeInput(attrs={
            'class': 'form-control',
            'type': 'datetime-local'
        })
    )
    
    titre_ouvrage = forms.CharField(
        label='Titre de l\'ouvrage',
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Rechercher un livre...'
        })
    )
    
    numero_inventaire = forms.CharField(
        label='Numéro d\'inventaire',
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Numéro d\'inventaire'
        })
    )
    
    ancien_code = forms.CharField(
        label='Ancien code',
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Ancien code (optionnel)'
        })
    )