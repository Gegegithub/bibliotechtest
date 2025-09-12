from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import InscriptionForm, ConnexionForm
from .supabase_service import SupabaseService
from .middleware import login_requis

def inscription(request):
    if request.method == "POST":
        form = InscriptionForm(request.POST)
        if form.is_valid():
            # Préparer les données pour Supabase
            user_data = {
                "nom": form.cleaned_data['nom'],
                "prenom": form.cleaned_data['prenom'],
                "adresse": form.cleaned_data.get('adresse', ''),
                "telephone": form.cleaned_data.get('telephone', ''),
                "secteur_activite": form.cleaned_data.get('secteur_activite', ''),
                "institution": form.cleaned_data.get('institution', ''),
                "profil": form.cleaned_data.get('type_utilisateur', 'etudiant'),
                "is_admin": False,
                "is_administration": False,
                "is_librarian": False,
                "is_user": True
            }
            
            # Utiliser Supabase pour l'inscription
            supabase_service = SupabaseService()
            result = supabase_service.sign_up(
                email=form.cleaned_data['email'],
                password=form.cleaned_data['mot_de_passe'],
                user_data=user_data
            )
            
            if result['success']:
                messages.success(request, "Inscription réussie ! Vous pouvez maintenant vous connecter.")
                return redirect('connexion')
            else:
                messages.error(request, f"Erreur lors de l'inscription: {result['error']}")
    else:
        form = InscriptionForm()
    
    return render(request, 'inscription.html', {'form': form})

def connexion(request):
    if request.method == 'POST':
        form = ConnexionForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            mot_de_passe = form.cleaned_data['mot_de_passe']
            
            # Utiliser Supabase pour la connexion
            supabase_service = SupabaseService()
            result = supabase_service.sign_in(email, mot_de_passe)
            
            if result['success']:
                # Créer une session pour l'utilisateur avec les données Supabase
                request.session['utilisateur_id'] = result['user'].id
                request.session['utilisateur_email'] = result['user'].email
                request.session['utilisateur_profile'] = result['profile']
                
                messages.success(request, "Vous êtes bien connecté(e) !")
                
                # Redirection selon le type d'utilisateur
                profile = result['profile']
                if profile and profile.get('is_librarian'):
                    return redirect('dashboard_bibliothecaire')
                elif profile and profile.get('is_admin'):
                    return redirect('dashboard_admin')
                else:
                    return redirect('accueil')
            else:
                messages.error(request, f"Erreur de connexion: {result['error']}")
    else:
        form = ConnexionForm()

    next_url = request.GET.get('next', '')
    return render(request, 'connexion.html', {'form': form, 'next': next_url})

def deconnexion(request):
    if 'utilisateur_id' in request.session:
        # Déconnexion de Supabase
        supabase_service = SupabaseService()
        supabase_service.sign_out()
        
        # Nettoyer la session Django
        request.session.flush()
        
    messages.info(request, "Vous avez été déconnecté(e).")
    return redirect('accueil')

@login_requis
def mon_compte(request):
    return render(request, 'mon_compte.html')

@login_requis
def dashboard_bibliothecaire(request):
    # Vérifier que l'utilisateur est bien un bibliothécaire
    profile = request.session.get('utilisateur_profile', {})
    if not profile.get('is_librarian'):
        messages.error(request, "Accès non autorisé.")
        return redirect('accueil')
    
    return render(request, 'dashboard_bibliothecaire.html', {'profile': profile})

@login_requis
def dashboard_admin(request):
    # Vérifier que l'utilisateur est bien un admin
    profile = request.session.get('utilisateur_profile', {})
    if not profile.get('is_admin'):
        messages.error(request, "Accès non autorisé.")
        return redirect('accueil')
    
    return render(request, 'dashboard_admin.html', {'profile': profile})