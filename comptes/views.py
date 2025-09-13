from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import InscriptionForm, ConnexionForm, RendezVousForm
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
                
                # Vérifier s'il y a une URL de redirection spécifiée
                next_url = request.POST.get('next') or request.GET.get('next', '')
                if next_url:
                    return redirect(next_url)
                
                # Redirection selon le type d'utilisateur (par défaut)
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

def rendez_vous(request):
    """Vue pour prendre rendez-vous"""
    if not request.session.get('utilisateur_profile'):
        try:
            messages.warning(request, "Vous devez être connecté pour prendre rendez-vous.")
        except:
            print("Vous devez être connecté pour prendre rendez-vous.")
        return redirect('connexion')
    
    # Récupérer les informations de l'utilisateur connecté
    profile = request.session.get('utilisateur_profile', {})
    
    # Pré-remplir le formulaire avec les données utilisateur
    initial_data = {
        'nom': profile.get('nom', ''),
        'prenom': profile.get('prenom', ''),
        'email': profile.get('email', ''),
        'telephone': profile.get('telephone', ''),
    }
    
    form = RendezVousForm(initial=initial_data)
    livres_similaires = []
    message_indispo = None
    
    if request.method == 'POST':
        form = RendezVousForm(request.POST)
        if form.is_valid():
            try:
                supabase_service = SupabaseService()
                
                # Vérifier si le livre existe
                titre_ouvrage = form.cleaned_data['titre_ouvrage']
                numero_inventaire = form.cleaned_data['numero_inventaire']
                
                # Rechercher le livre par titre et numéro d'inventaire
                livres = supabase_service.search_livres(titre_ouvrage)
                livre_trouve = None
                
                for livre in livres:
                    if livre.get('numero_inventaire') == numero_inventaire:
                        livre_trouve = livre
                        break
                
                if not livre_trouve:
                    # Si le livre n'est pas trouvé, chercher des livres similaires
                    livres_similaires = livres[:5]  # Limiter à 5 suggestions
                    message_indispo = f"L'ouvrage '{titre_ouvrage}' avec le numéro d'inventaire '{numero_inventaire}' n'a pas été trouvé."
                    form = RendezVousForm(request.POST)  # Recharger le formulaire avec les données
                else:
                    # Créer le rendez-vous
                    user_id = request.session.get('utilisateur_id')
                    profile = request.session.get('utilisateur_profile', {})
                    
                    rendez_vous_data = {
                        'user_id': user_id,
                        'profil': form.cleaned_data['profil'],
                        'raison': form.cleaned_data['raison'],
                        'appointment_date': form.cleaned_data['appointment_date'].isoformat(),
                        'titre_ouvrage': form.cleaned_data['titre_ouvrage'],
                        'numero_inventaire': form.cleaned_data['numero_inventaire'],
                        'ancien_code': form.cleaned_data.get('ancien_code', ''),
                        'statut': 'en_attente',
                        'nom': profile.get('nom', ''),
                        'prenom': profile.get('prenom', ''),
                        'email': profile.get('email', ''),
                        'telephone': profile.get('telephone', '')
                    }
                    
                    # Sauvegarder le rendez-vous dans Supabase
                    result = supabase_service.create_rendez_vous(rendez_vous_data)
                    
                    if result:
                        try:
                            messages.success(request, "Votre demande de rendez-vous a été enregistrée avec succès. Vous serez notifié de la réponse.")
                        except:
                            print("Votre demande de rendez-vous a été enregistrée avec succès.")
                        return redirect('accueil')
                    else:
                        try:
                            messages.error(request, "Erreur lors de l'enregistrement du rendez-vous.")
                        except:
                            print("Erreur lors de l'enregistrement du rendez-vous.")
                            
            except Exception as e:
                print(f"Erreur lors de la création du rendez-vous: {e}")
                try:
                    messages.error(request, "Une erreur est survenue lors de l'enregistrement du rendez-vous.")
                except:
                    print("Une erreur est survenue lors de l'enregistrement du rendez-vous.")
    
    # Si c'est une requête GET avec des paramètres de livre (depuis la page de détail)
    elif request.method == 'GET':
        livre_titre = request.GET.get('livre_titre')
        livre_inventaire = request.GET.get('livre_inventaire')
        livre_ancien_code = request.GET.get('livre_ancien_code')
        
        if livre_titre and livre_inventaire:
            # Mettre à jour les données initiales avec les informations du livre
            initial_data.update({
                'titre_ouvrage': livre_titre,
                'numero_inventaire': livre_inventaire,
                'ancien_code': livre_ancien_code or ''
            })
            form = RendezVousForm(initial=initial_data)
    
    return render(request, 'rendez_vous.html', {
        'form': form,
        'livres_similaires': livres_similaires,
        'message_indispo': message_indispo
    })

def gestion_rdv_bibliothecaire(request):
    """Vue pour la gestion des rendez-vous par les bibliothécaires"""
    if not request.session.get('utilisateur_profile'):
        try:
            messages.warning(request, "Vous devez être connecté pour accéder à cette page.")
        except:
            print("Vous devez être connecté pour accéder à cette page.")
        return redirect('connexion')
    
    # Vérifier si l'utilisateur est bibliothécaire
    profile = request.session.get('utilisateur_profile', {})
    if not profile.get('is_librarian', False):
        try:
            messages.error(request, "Vous n'avez pas les droits pour accéder à cette page.")
        except:
            print("Vous n'avez pas les droits pour accéder à cette page.")
        return redirect('accueil')
    
    try:
        supabase_service = SupabaseService()
        
        # Récupérer tous les rendez-vous
        rendez_vous = supabase_service.get_all_rendez_vous()
        
        return render(request, 'gestion_rdv_bibliothecaire.html', {
            'rendez_vous': rendez_vous
        })
        
    except Exception as e:
        print(f"Erreur lors de la récupération des rendez-vous: {e}")
        try:
            messages.error(request, "Erreur lors du chargement des rendez-vous.")
        except:
            print("Erreur lors du chargement des rendez-vous.")
        return redirect('dashboard_bibliothecaire')