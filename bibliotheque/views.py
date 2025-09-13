from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from django.views.decorators.http import require_POST
from comptes.supabase_service import SupabaseService
from comptes.middleware import login_requis, permission_requise
from .forms import CategorieForm, LivreForm

def home(request):
    """
    Vue d'accueil utilisant Supabase
    """
    try:
        # Utiliser Supabase pour récupérer les données
        supabase_service = SupabaseService()
        
        # Récupérer les catégories depuis Supabase
        list_categories = supabase_service.get_all_categories()
        categories_existent = len(list_categories) > 0
        
        # Pour chaque catégorie, récupérer ses livres
        for categorie in list_categories:
            livres_categorie = supabase_service.get_livres_by_categorie(categorie['id'])
            categorie['livres'] = livres_categorie
            categorie['nombre_livres'] = len(livres_categorie)
        
        # Récupérer tous les livres pour les statistiques
        list_livres = supabase_service.get_all_livres()
        livres_existent = len(list_livres) > 0
        
    except Exception as e:
        print(f"Erreur lors de la récupération des données: {e}")
        list_categories = []
        list_livres = []
        categories_existent = False
        livres_existent = False
    
    # Gestion robuste de est_bibliothecaire
    if hasattr(request, 'utilisateur') and request.utilisateur:
        est_bibliothecaire = request.utilisateur.est_bibliothecaire
    else:
        est_bibliothecaire = False
    
    return render(request, "index.html", {
        "list_categories": list_categories,
        "list_livres": list_livres,
        "est_bibliothecaire": est_bibliothecaire,
        "categories_existent": categories_existent,
        "livres_existent": livres_existent
    })

def accueil(request):
    """
    Vue d'accueil - Page d'introduction avec bouton vers le catalogue
    """
    return render(request, 'accueil.html')

def presentation_bibliotheque(request):
    return render(request, 'presentation_bibliotheque.html')

def details_categorie(request, categorie_id):
    try:
        # Utiliser Supabase pour récupérer la catégorie
        supabase_service = SupabaseService()
        categorie = supabase_service.get_categorie_by_id(categorie_id)
        
        if not categorie:
            messages.error(request, "Catégorie non trouvée.")
            return redirect('accueil')
        
        # Récupérer les livres de cette catégorie
        livres = supabase_service.get_livres_by_categorie(categorie_id)
        livres_existent = len(livres) > 0
        
    except Exception as e:
        print(f"Erreur lors de la récupération des données: {e}")
        messages.error(request, "Erreur lors du chargement de la catégorie.")
        return redirect('accueil')
    
    # Gestion robuste de est_bibliothecaire
    if hasattr(request, 'utilisateur') and request.utilisateur:
        est_bibliothecaire = request.utilisateur.est_bibliothecaire
    else:
        est_bibliothecaire = False
    
    return render(request, "details.html", {
        "categorie": categorie,
        "livres": livres,
        "est_bibliothecaire": est_bibliothecaire,
        "livres_existent": livres_existent
    })

def demander_connexion_detail(request, categorie_id, livre_id):
    """Vue pour demander la connexion avant d'accéder aux détails d'un livre"""
    messages.warning(request, "Veuillez vous connecter pour consulter ce livre.")
    from django.urls import reverse
    next_url = reverse('detail_livre', kwargs={'categorie_id': categorie_id, 'livre_id': livre_id})
    return redirect(f"/comptes/connexion/?next={next_url}")

def detail_livre(request, categorie_id, livre_id):
    """Vue pour afficher les détails d'un livre"""
    
    # Vérification de l'authentification
    if not request.session.get('utilisateur_profile'):
        return demander_connexion_detail(request, categorie_id, livre_id)
    
    try:
        supabase_service = SupabaseService()
        
        # Récupérer le livre
        livre = supabase_service.get_livre_by_id(livre_id)
        if not livre:
            messages.error(request, "Livre non trouvé.")
            return redirect('details_categorie', categorie_id=categorie_id)
        
        # Récupérer la catégorie
        categorie = supabase_service.get_categorie_by_id(categorie_id)
        if not categorie:
            messages.error(request, "Catégorie non trouvée.")
            return redirect('accueil')
        
        # Vérifier si le livre est en favori
        user_id = request.session.get('utilisateur_id')
        est_favori = False
        if user_id:
            try:
                favoris = supabase_service.get_favoris_utilisateur(user_id)
                est_favori = any(f['livre_id'] == livre_id for f in favoris)
            except Exception as e:
                print(f"Erreur lors de la vérification des favoris: {e}")
        
    except Exception as e:
        print(f"Erreur lors de la récupération du livre: {e}")
        messages.error(request, "Erreur lors du chargement du livre.")
        return redirect('accueil')
    
    # Gestion robuste de est_bibliothecaire
    if hasattr(request, 'utilisateur') and request.utilisateur:
        est_bibliothecaire = request.utilisateur.est_bibliothecaire
    else:
        est_bibliothecaire = False
    
    return render(request, 'detail_livre.html', {
        'categorie': categorie,
        'livre': livre,
        'est_favori': est_favori,
        'est_bibliothecaire': est_bibliothecaire
    })

@require_POST
def ajouter_favori(request, livre_id):
    """Vue pour ajouter un livre aux favoris"""
    if not request.session.get('utilisateur_profile'):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Vous devez être connecté pour ajouter des favoris.'})
        try:
            messages.warning(request, "Vous devez être connecté pour ajouter des favoris.")
        except:
            print("Vous devez être connecté pour ajouter des favoris.")
        return redirect('connexion')
    
    try:
        supabase_service = SupabaseService()
        user_id = request.session.get('utilisateur_id')
        
        if not user_id:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Erreur d\'authentification.'})
            try:
                messages.error(request, "Erreur d'authentification.")
            except:
                print("Erreur d'authentification.")
            return redirect('connexion')
        
        # Vérifier si le livre existe
        livre = supabase_service.get_livre_by_id(livre_id)
        if not livre:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Livre non trouvé.'})
            try:
                messages.error(request, "Livre non trouvé.")
            except:
                print("Livre non trouvé.")
            return redirect('accueil')
        
        # Vérifier si le livre est déjà en favori
        favoris = supabase_service.get_favoris_utilisateur(user_id)
        est_deja_favori = any(f['livre_id'] == livre_id for f in favoris)
        
        if est_deja_favori:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Livre déjà dans les favoris'})
            try:
                messages.info(request, "Livre déjà dans les favoris")
            except:
                print("Livre déjà dans les favoris")
        else:
            # Ajouter le livre aux favoris
            result = supabase_service.ajouter_favori(user_id, livre_id)
            
            if result:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': True, 'message': 'Ajouté'})
                try:
                    messages.success(request, "Livre ajouté aux favoris !")
                except:
                    print("Livre ajouté aux favoris !")
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': 'Erreur lors de l\'ajout aux favoris.'})
                try:
                    messages.error(request, "Erreur lors de l'ajout aux favoris.")
                except:
                    print("Erreur lors de l'ajout aux favoris.")
            
    except Exception as e:
        print(f"Erreur lors de l'ajout aux favoris: {e}")
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Erreur lors de l\'ajout aux favoris.'})
        try:
            messages.error(request, "Erreur lors de l'ajout aux favoris.")
        except:
            print("Erreur lors de l'ajout aux favoris.")
    
    # Rediriger vers la page précédente ou vers mes favoris
    return redirect(request.META.get('HTTP_REFERER', 'mes_favoris'))

@require_POST
def supprimer_favori(request, livre_id):
    """Vue pour supprimer un livre des favoris"""
    if not request.session.get('utilisateur_profile'):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Vous devez être connecté pour gérer vos favoris.'})
        try:
            messages.warning(request, "Vous devez être connecté pour gérer vos favoris.")
        except:
            print("Vous devez être connecté pour gérer vos favoris.")
        return redirect('connexion')
    
    try:
        supabase_service = SupabaseService()
        user_id = request.session.get('utilisateur_id')
        
        if not user_id:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Erreur d\'authentification.'})
            try:
                messages.error(request, "Erreur d'authentification.")
            except:
                print("Erreur d'authentification.")
            return redirect('connexion')
        
        # Vérifier si le livre existe
        livre = supabase_service.get_livre_by_id(livre_id)
        if not livre:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Livre non trouvé.'})
            try:
                messages.error(request, "Livre non trouvé.")
            except:
                print("Livre non trouvé.")
            return redirect('accueil')
        
        # Vérifier si le livre est en favori
        favoris = supabase_service.get_favoris_utilisateur(user_id)
        est_en_favori = any(f['livre_id'] == livre_id for f in favoris)
        
        if not est_en_favori:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'message': 'Livre non présent dans les favoris'})
            try:
                messages.info(request, "Livre non présent dans les favoris")
            except:
                print("Livre non présent dans les favoris")
        else:
            # Supprimer le livre des favoris
            result = supabase_service.supprimer_favori(user_id, livre_id)
            
            if result:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': True, 'message': 'Supprimé'})
                try:
                    messages.success(request, "Livre supprimé des favoris !")
                except:
                    print("Livre supprimé des favoris !")
            else:
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'message': 'Erreur lors de la suppression des favoris.'})
                try:
                    messages.error(request, "Erreur lors de la suppression des favoris.")
                except:
                    print("Erreur lors de la suppression des favoris.")
            
    except Exception as e:
        print(f"Erreur lors de la suppression des favoris: {e}")
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Erreur lors de la suppression des favoris.'})
        try:
            messages.error(request, "Erreur lors de la suppression des favoris.")
        except:
            print("Erreur lors de la suppression des favoris.")
    
    # Rediriger vers la page précédente ou vers mes favoris
    return redirect(request.META.get('HTTP_REFERER', 'mes_favoris'))

def ajouter_categorie(request):
    """Vue pour ajouter une catégorie"""
    if not request.session.get('utilisateur_profile'):
        messages.warning(request, "Vous devez être connecté pour ajouter une catégorie.")
        return redirect('connexion')
    
    # Vérifier si l'utilisateur est bibliothécaire
    profile = request.session.get('utilisateur_profile', {})
    if not profile.get('is_librarian', False):
        messages.error(request, "Vous n'avez pas les droits pour ajouter une catégorie.")
        return redirect('accueil')
    
    if request.method == 'POST':
        form = CategorieForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                supabase_service = SupabaseService()
                
                # Préparer les données pour Supabase
                categorie_data = {
                    'nom': form.cleaned_data['nom'],
                }
                
                # Gérer l'image si elle est fournie
                if form.cleaned_data.get('image'):
                    categorie_data['image'] = form.cleaned_data['image']
                
                # Créer la catégorie dans Supabase
                result = supabase_service.create_categorie(categorie_data)
                
                if result:
                    try:
                        messages.success(request, "Catégorie ajoutée avec succès !")
                    except:
                        print("Catégorie ajoutée avec succès !")
                    return redirect('catalogue')
                else:
                    try:
                        messages.error(request, "Erreur lors de l'ajout de la catégorie.")
                    except:
                        print("Erreur lors de l'ajout de la catégorie.")
                    
            except Exception as e:
                print(f"Erreur lors de l'ajout de la catégorie: {e}")
                try:
                    messages.error(request, f"Erreur lors de l'ajout de la catégorie: {e}")
                except:
                    print(f"Erreur lors de l'ajout de la catégorie: {e}")
    else:
        form = CategorieForm()
    
    return render(request, 'ajouter_categorie.html', {'form': form})

def modifier_categorie(request, categorie_id):
    """Vue pour modifier une catégorie"""
    if not request.session.get('utilisateur_profile'):
        messages.warning(request, "Vous devez être connecté pour modifier une catégorie.")
        return redirect('connexion')
    
    # Vérifier si l'utilisateur est bibliothécaire
    profile = request.session.get('utilisateur_profile', {})
    if not profile.get('is_librarian', False):
        messages.error(request, "Vous n'avez pas les droits pour modifier une catégorie.")
        return redirect('accueil')
    
    try:
        supabase_service = SupabaseService()
        
        # Récupérer la catégorie existante
        categorie = supabase_service.get_categorie_by_id(categorie_id)
        if not categorie:
            messages.error(request, "Catégorie non trouvée.")
            return redirect('catalogue')
        
        if request.method == 'POST':
            form = CategorieForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    # Préparer les données pour Supabase
                    categorie_data = {
                        'nom': form.cleaned_data['nom'],
                    }
                    
                    # Gérer l'image si elle est fournie
                    if form.cleaned_data.get('image'):
                        categorie_data['image'] = form.cleaned_data['image']
                    
                    # Mettre à jour la catégorie dans Supabase
                    result = supabase_service.update_categorie(categorie_id, categorie_data)
                    
                    if result:
                        try:
                            messages.success(request, "Catégorie modifiée avec succès !")
                        except:
                            print("Catégorie modifiée avec succès !")
                        return redirect('catalogue')
                    else:
                        try:
                            messages.error(request, "Erreur lors de la modification de la catégorie.")
                        except:
                            print("Erreur lors de la modification de la catégorie.")
                        
                except Exception as e:
                    print(f"Erreur lors de la modification de la catégorie: {e}")
                    try:
                        messages.error(request, f"Erreur lors de la modification de la catégorie: {e}")
                    except:
                        print(f"Erreur lors de la modification de la catégorie: {e}")
        else:
            # Pré-remplir le formulaire avec les données existantes
            form = CategorieForm(initial={
                'nom': categorie.get('nom', ''),
                'image': categorie.get('image', ''),
            })
        
        return render(request, 'modifier_categorie.html', {
            'form': form,
            'categorie': categorie
        })
        
    except Exception as e:
        print(f"Erreur lors de la récupération de la catégorie: {e}")
        try:
            messages.error(request, "Erreur lors du chargement de la catégorie.")
        except:
            print("Erreur lors du chargement de la catégorie.")
        return redirect('catalogue')

def supprimer_categorie(request, categorie_id):
    """Vue pour supprimer une catégorie"""
    if not request.session.get('utilisateur_profile'):
        messages.warning(request, "Vous devez être connecté pour supprimer une catégorie.")
        return redirect('connexion')
    
    # Vérifier si l'utilisateur est bibliothécaire
    profile = request.session.get('utilisateur_profile', {})
    if not profile.get('is_librarian', False):
        messages.error(request, "Vous n'avez pas les droits pour supprimer une catégorie.")
        return redirect('accueil')
    
    if request.method == 'POST':
        try:
            supabase_service = SupabaseService()
            
            # Vérifier que la catégorie existe
            categorie = supabase_service.get_categorie_by_id(categorie_id)
            if not categorie:
                messages.error(request, "Catégorie non trouvée.")
                return redirect('catalogue')
            
            # Vérifier s'il y a des livres dans cette catégorie
            livres = supabase_service.get_livres_by_categorie(categorie_id)
            if livres:
                messages.error(request, f"Impossible de supprimer la catégorie '{categorie['nom']}' car elle contient {len(livres)} livre(s). Supprimez d'abord les livres de cette catégorie.")
                return redirect('catalogue')
            
            # Supprimer la catégorie
            result = supabase_service.delete_categorie(categorie_id)
            
            if result:
                messages.success(request, f"Catégorie '{categorie['nom']}' supprimée avec succès !")
            else:
                messages.error(request, "Erreur lors de la suppression de la catégorie.")
                
        except Exception as e:
            print(f"Erreur lors de la suppression de la catégorie: {e}")
            messages.error(request, f"Erreur lors de la suppression de la catégorie: {e}")
    
    return redirect('catalogue')

def ajouter_livre(request, categorie_id):
    """Vue pour ajouter un livre"""
    if not request.session.get('utilisateur_profile'):
        try:
            messages.warning(request, "Vous devez être connecté pour ajouter un livre.")
        except:
            print("Vous devez être connecté pour ajouter un livre.")
        return redirect('connexion')
    
    # Vérifier si l'utilisateur est bibliothécaire
    profile = request.session.get('utilisateur_profile', {})
    if not profile.get('is_librarian', False):
        try:
            messages.error(request, "Vous n'avez pas les droits pour ajouter un livre.")
        except:
            print("Vous n'avez pas les droits pour ajouter un livre.")
        return redirect('accueil')
    
    try:
        supabase_service = SupabaseService()
        
        # Récupérer la catégorie
        categorie = supabase_service.get_categorie_by_id(categorie_id)
        if not categorie:
            try:
                messages.error(request, "Catégorie non trouvée.")
            except:
                print("Catégorie non trouvée.")
            return redirect('catalogue')
        
        if request.method == 'POST':
            form = LivreForm(request.POST, request.FILES)
            if form.is_valid():
                try:
                    # Récupérer ou créer l'auteur
                    auteur_nom = form.cleaned_data['auteur_texte']
                    auteur = supabase_service.get_auteur_by_name(auteur_nom)
                    
                    if not auteur:
                        # Créer un nouvel auteur
                        auteur_data = {
                            'nom': auteur_nom,
                            'prenom': ''  # On peut améliorer cela plus tard
                        }
                        auteur = supabase_service.create_auteur(auteur_data)
                        if not auteur:
                            try:
                                messages.error(request, "Erreur lors de la création de l'auteur.")
                            except:
                                print("Erreur lors de la création de l'auteur.")
                            return render(request, 'ajouter_livre.html', {
                                'form': form,
                                'categorie': categorie
                            })
                    
                    # Préparer les données du livre
                    livre_data = {
                        'titre': form.cleaned_data['titre'],
                        'auteur_id': auteur['id'],
                        'categorie_id': categorie_id,
                        'description': form.cleaned_data.get('description', ''),
                        'numero_inventaire': form.cleaned_data['numero_inventaire'],
                        'ancien_code': form.cleaned_data.get('ancien_code', ''),
                        'date_publication': form.cleaned_data['date_publication'].strftime('%Y-%m-%d'),
                    }
                    
                    # Gérer l'image si elle est fournie
                    if form.cleaned_data.get('image'):
                        # Ici, vous devriez uploader l'image vers Supabase Storage
                        # Pour l'instant, on stocke juste le nom du fichier
                        livre_data['image'] = form.cleaned_data['image'].name
                    
                    # Créer le livre
                    result = supabase_service.create_livre(livre_data)
                    
                    if result:
                        try:
                            messages.success(request, "Livre ajouté avec succès !")
                        except:
                            print("Livre ajouté avec succès !")
                        return redirect('details_categorie', categorie_id=categorie_id)
                    else:
                        try:
                            messages.error(request, "Erreur lors de l'ajout du livre.")
                        except:
                            print("Erreur lors de l'ajout du livre.")
                            
                except Exception as e:
                    print(f"Erreur lors de l'ajout du livre: {e}")
                    try:
                        messages.error(request, f"Erreur lors de l'ajout du livre: {e}")
                    except:
                        print(f"Erreur lors de l'ajout du livre: {e}")
        else:
            form = LivreForm(initial={'categorie_id': categorie_id})
        
        return render(request, 'ajouter_livre.html', {
            'form': form,
            'categorie': categorie
        })
        
    except Exception as e:
        print(f"Erreur lors du chargement de la page d'ajout de livre: {e}")
        try:
            messages.error(request, "Erreur lors du chargement de la page.")
        except:
            print("Erreur lors du chargement de la page.")
        return redirect('catalogue')

def modifier_livre(request, livre_id):
    """Vue pour modifier un livre (placeholder)"""
    if not request.session.get('utilisateur_profile'):
        messages.warning(request, "Vous devez être connecté pour modifier un livre.")
        return redirect('connexion')
    
    # Vérifier si l'utilisateur est bibliothécaire
    profile = request.session.get('utilisateur_profile', {})
    if not profile.get('is_librarian', False):
        messages.error(request, "Vous n'avez pas les droits pour modifier un livre.")
        return redirect('accueil')
    
    messages.info(request, "Fonctionnalité de modification de livre en cours de développement.")
    return redirect('catalogue')

def supprimer_livre(request, livre_id):
    """Vue pour supprimer un livre"""
    if not request.session.get('utilisateur_profile'):
        try:
            messages.warning(request, "Vous devez être connecté pour supprimer un livre.")
        except:
            print("Vous devez être connecté pour supprimer un livre.")
        return redirect('connexion')
    
    # Vérifier si l'utilisateur est bibliothécaire
    profile = request.session.get('utilisateur_profile', {})
    if not profile.get('is_librarian', False):
        try:
            messages.error(request, "Vous n'avez pas les droits pour supprimer un livre.")
        except:
            print("Vous n'avez pas les droits pour supprimer un livre.")
        return redirect('accueil')
    
    if request.method == 'POST':
        try:
            supabase_service = SupabaseService()
            
            # Récupérer le livre pour obtenir la catégorie
            livre = supabase_service.get_livre_by_id(livre_id)
            if not livre:
                try:
                    messages.error(request, "Livre non trouvé.")
                except:
                    print("Livre non trouvé.")
                return redirect('catalogue')
            
            # Supprimer le livre
            result = supabase_service.delete_livre(livre_id)
            
            if result:
                try:
                    messages.success(request, f"Livre '{livre['titre']}' supprimé avec succès !")
                except:
                    print(f"Livre '{livre['titre']}' supprimé avec succès !")
                
                # Rediriger vers la catégorie du livre
                categorie_id = livre.get('categorie_id')
                if categorie_id:
                    return redirect('details_categorie', categorie_id=categorie_id)
                else:
                    return redirect('catalogue')
            else:
                try:
                    messages.error(request, "Erreur lors de la suppression du livre.")
                except:
                    print("Erreur lors de la suppression du livre.")
                
        except Exception as e:
            print(f"Erreur lors de la suppression du livre: {e}")
            try:
                messages.error(request, f"Erreur lors de la suppression du livre: {e}")
            except:
                print(f"Erreur lors de la suppression du livre: {e}")
    
    # Si ce n'est pas une requête POST, rediriger vers le catalogue
    return redirect('catalogue')

def mes_favoris(request):
    """Vue pour afficher les favoris de l'utilisateur"""
    if not request.session.get('utilisateur_profile'):
        try:
            messages.warning(request, "Vous devez être connecté pour voir vos favoris.")
        except:
            print("Vous devez être connecté pour voir vos favoris.")
        return redirect('connexion')
    
    try:
        supabase_service = SupabaseService()
        user_id = request.session.get('utilisateur_id')
        
        if not user_id:
            try:
                messages.error(request, "Erreur d'authentification.")
            except:
                print("Erreur d'authentification.")
            return redirect('connexion')
        
        # Récupérer les favoris de l'utilisateur
        favoris = supabase_service.get_favoris_utilisateur(user_id)
        
        # Récupérer les détails complets des livres favoris
        livres_favoris = []
        for favori in favoris:
            livre = supabase_service.get_livre_by_id(favori['livre_id'])
            if livre:
                livres_favoris.append(livre)
        
        return render(request, 'mes_favoris.html', {
            'livres_favoris': livres_favoris
        })
        
    except Exception as e:
        print(f"Erreur lors de la récupération des favoris: {e}")
        try:
            messages.error(request, "Erreur lors du chargement de vos favoris.")
        except:
            print("Erreur lors du chargement de vos favoris.")
        return redirect('accueil')

def recherche(request):
    """Vue pour la recherche de livres"""
    query = request.GET.get('q', '').strip()
    
    if query and len(query) >= 2:  # Minimum 2 caractères pour la recherche
        try:
            supabase_service = SupabaseService()
            resultats = supabase_service.search_livres(query)
            
            # Log de la recherche pour le débogage
            print(f"Recherche pour '{query}': {len(resultats)} résultats trouvés")
            
        except Exception as e:
            print(f"Erreur lors de la recherche: {e}")
            resultats = []
            try:
                messages.error(request, "Erreur lors de la recherche. Veuillez réessayer.")
            except:
                print("Erreur lors de la recherche. Veuillez réessayer.")
    elif query and len(query) < 2:
        resultats = []
        try:
            messages.warning(request, "Veuillez saisir au moins 2 caractères pour la recherche.")
        except:
            print("Veuillez saisir au moins 2 caractères pour la recherche.")
    else:
        resultats = []

    return render(request, 'recherche_resultats.html', {
        'livres': resultats,
        'query': query,
        'nombre_resultats': len(resultats)
    })

def recherche_suggestions(request):
    """Vue pour les suggestions de recherche en temps réel"""
    query = request.GET.get('q', '').strip()
    suggestions = []

    if query and len(query) >= 2:  # Minimum 2 caractères pour les suggestions
        try:
            supabase_service = SupabaseService()
            
            # Recherche dans les titres de livres
            livres = supabase_service.search_livres(query)
            titres_livres = [livre['titre'] for livre in livres[:5]]
            
            # Recherche dans les noms d'auteurs
            auteurs = supabase_service.search_auteurs(query)
            noms_auteurs = []
            for auteur in auteurs[:5]:
                nom_complet = f"{auteur.get('prenom', '')} {auteur.get('nom', '')}".strip()
                if nom_complet:
                    noms_auteurs.append(nom_complet)
            
            # Recherche dans les catégories
            categories = supabase_service.search_categories(query)
            noms_categories = [cat['nom'] for cat in categories[:5]]
            
            # Combiner toutes les suggestions et supprimer les doublons
            suggestions = list(set(
                titres_livres + noms_auteurs + noms_categories
            ))[:10]
            
        except Exception as e:
            print(f"Erreur lors de la récupération des suggestions: {e}")
            suggestions = []

    return JsonResponse(suggestions, safe=False)

def autocomplete(request):
    """Vue pour l'autocomplétion (compatible avec jQuery UI)"""
    if 'term' in request.GET:
        term = request.GET.get('term', '').strip()
        suggestions = []
        
        if term and len(term) >= 2:
            try:
                supabase_service = SupabaseService()
                
                # Recherche dans les titres de livres
                livres = supabase_service.search_livres(term)
                suggestions = [livre['titre'] for livre in livres[:10]]
                
            except Exception as e:
                print(f"Erreur lors de l'autocomplétion: {e}")
                suggestions = []
        
        return JsonResponse(suggestions, safe=False)
    
    return JsonResponse([], safe=False)