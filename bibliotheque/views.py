from django.shortcuts import render, redirect
from comptes.supabase_service import SupabaseService
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse
from comptes.middleware import login_requis, permission_requise

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
        
        # Récupérer les livres depuis Supabase
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

def recherche(request):
    query = request.GET.get('q', '')
    
    if query:
        try:
            supabase_service = SupabaseService()
            resultats = supabase_service.search_livres(query)
        except Exception as e:
            print(f"Erreur lors de la recherche: {e}")
            resultats = []
    else:
        resultats = []

    return render(request, 'recherche_resultats.html', {
        'livres': resultats,
        'query': query
    })