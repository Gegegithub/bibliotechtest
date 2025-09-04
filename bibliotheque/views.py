from django.shortcuts import render, get_object_or_404, redirect
from .models import Categorie, Livre
from comptes.models import Utilisateur
from django.db.models import Q
from django.http import JsonResponse
from django.contrib import messages
from django.urls import reverse
from django.utils.http import urlencode
from django.views.decorators.http import require_POST
from .forms import CategorieForm, LivreForm
from comptes.middleware import login_requis, permission_requise
import wikipedia
wikipedia.set_lang("fr")  # pour le français

def home(request):
    """
    Vue d'accueil avec gestion robuste des cas où les tables n'existent pas encore
    """
    # Vérification de l'existence des tables et récupération des données
    from django.db import connection
    
    # Vérifier si la table Categorie existe
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bibliotheque_categorie'")
        table_categorie_exists = cursor.fetchone() is not None
        
        if table_categorie_exists:
            list_categories = Categorie.objects.all()
            categories_existent = list_categories.exists()
        else:
            list_categories = []
            categories_existent = False
            
    except Exception:
        list_categories = []
        categories_existent = False
    
    # Vérifier si la table Livre existe
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bibliotheque_livre'")
        table_livre_exists = cursor.fetchone() is not None
        
        if table_livre_exists:
            list_livres = Livre.objects.all()
            livres_existent = list_livres.exists()
        else:
            list_livres = []
            livres_existent = False
            
    except Exception:
        list_livres = []
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

@permission_requise('bibliothecaire')
def ajouter_categorie(request):
    if request.method == "POST":
        form = CategorieForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Catégorie ajoutée avec succès !")
            return redirect('catalogue')  # redirige vers le catalogue
    else:
        form = CategorieForm()
    return render(request, 'ajouter_categorie.html', {'form': form})

def details_categorie(request, categorie_id):
    categorie = get_object_or_404(Categorie, id=categorie_id)
    
    # Récupération des livres avec gestion des cas vides
    try:
        livres = Livre.objects.filter(categorie=categorie)
        livres_existent = livres.exists()
    except Exception:
        livres = []
        livres_existent = False
    
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

@login_requis
@permission_requise('bibliothecaire')
def ajouter_livre(request, categorie_id):
    categorie = get_object_or_404(Categorie, pk=categorie_id)
    if request.method == 'POST':
        form = LivreForm(request.POST, request.FILES)
        if form.is_valid():
            livre = form.save(commit=False)
            livre.categorie = categorie
            livre.save()
            messages.success(request, "Livre ajouté avec succès !")
            return redirect('details_categorie', categorie.id)
    else:
        form = LivreForm()
    return render(request, 'ajouter_livre.html', {'form': form, 'categorie': categorie})

@permission_requise('bibliothecaire')
def supprimer_categorie(request, categorie_id):
    if request.method == 'POST':
        categorie = get_object_or_404(Categorie, id=categorie_id)
        nom_categorie = categorie.nom
        categorie.delete()
        messages.success(request, f"Catégorie '{nom_categorie}' supprimée avec succès !")
    return redirect('catalogue')

@permission_requise('bibliothecaire')
def modifier_categorie(request, categorie_id):
    categorie = get_object_or_404(Categorie, id=categorie_id)
    if request.method == 'POST':
        form = CategorieForm(request.POST, request.FILES, instance=categorie)
        if form.is_valid():
            form.save()
            messages.success(request, "Catégorie modifiée avec succès !")
            return redirect('catalogue')
    else:
        form = CategorieForm(instance=categorie)
    return render(request, 'modifier_categorie.html', {'form': form, 'categorie': categorie})

@permission_requise('bibliothecaire')
def supprimer_livre(request, livre_id):
    if request.method == 'POST':
        livre = get_object_or_404(Livre, id=livre_id)
        categorie_id = livre.categorie.id
        titre_livre = livre.titre
        livre.delete()
        messages.success(request, f"Livre '{titre_livre}' supprimé avec succès !")
        return redirect('details_categorie', categorie_id=categorie_id)
    return redirect('catalogue')

@login_requis
@permission_requise('bibliothecaire')
def modifier_livre(request, livre_id):
    livre = get_object_or_404(Livre, id=livre_id)
    
    if request.method == 'POST':
        form = LivreForm(request.POST, request.FILES, instance=livre)
        if form.is_valid():
            form.save()
            messages.success(request, "Livre modifié avec succès !")
            return redirect('details_categorie', categorie_id=livre.categorie.id)
    else:
        form = LivreForm(instance=livre)

    return render(request, 'modifier_livre.html', {'form': form, 'livre': livre})

@login_requis
def detail_livre(request, categorie_id, livre_id):
    categorie = get_object_or_404(Categorie, id=categorie_id)
    livre = get_object_or_404(Livre, id=livre_id, categorie_id=categorie_id)
    
    # Récupération des autres livres de la même catégorie
    try:
        autres_livres = Livre.objects.filter(categorie_id=categorie_id).exclude(id=livre_id)
    except Exception:
        autres_livres = []

    utilisateur = request.utilisateur
    est_favori = livre in utilisateur.favoris.all() if utilisateur else False

    description = livre.description or ""

    if livre.auteur:
        author_name = f"{livre.auteur.prenom or ''} {livre.auteur.nom}".strip()
        wiki_url = f"https://fr.wikipedia.org/wiki/{author_name.replace(' ', '_')}"
        # Essayer de récupérer un résumé depuis Wikipédia
        if not description:
            try:
                description = wikipedia.summary(author_name, sentences=3, auto_suggest=False)
            except Exception:
                description = "Pas de description disponible."
    else:
        wiki_url = None

    depuis_favoris = request.GET.get('depuis') == 'favoris'

    return render(request, 'detail_livre.html', {
        'categorie': categorie,
        'livre': livre,
        'autres_livres': None if depuis_favoris else autres_livres,
        'wiki_url': wiki_url,
        'est_favori': est_favori,
        'depuis_favoris': depuis_favoris,
        'description': description,
    })

def demander_connexion_detail(request, categorie_id, livre_id):
    messages.warning(request, "Veuillez vous connecter pour consulter ce livre.")
    next_url = reverse('detail_livre', kwargs={'categorie_id': categorie_id, 'livre_id': livre_id})
    return redirect(f"/comptes/connexion/?next={next_url}")

def recherche(request):
    query = request.GET.get('q', '')
    
    # Vérifier si la table Livre existe
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bibliotheque_livre'")
        table_livre_exists = cursor.fetchone() is not None
        
        if table_livre_exists:
            resultats = Livre.objects.all()
            if query:
                resultats = resultats.filter(
                    Q(titre__icontains=query) |
                    Q(auteur__nom__icontains=query) |
                    Q(auteur__prenom__icontains=query) |
                    Q(description__icontains=query)
                )
        else:
            resultats = []
    except Exception:
        resultats = []

    return render(request, 'recherche_resultats.html', {
        'livres': resultats,
        'query': query
    })

def recherche_suggestions(request):
    query = request.GET.get('q', '')
    suggestions = []

    if query:
        try:
            from django.db import connection
            cursor = connection.cursor()
            
            # Vérifier les tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bibliotheque_livre'")
            table_livre_exists = cursor.fetchone() is not None
            
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bibliotheque_categorie'")
            table_categorie_exists = cursor.fetchone() is not None
            
            if table_livre_exists:
                livres = Livre.objects.filter(titre__icontains=query)[:5]
                auteurs_livres = Livre.objects.filter(
                    Q(auteur__nom__icontains=query) | Q(auteur__prenom__icontains=query)
                )[:5]

                auteurs = []
                for livre in auteurs_livres:
                    auteur = livre.auteur
                    if auteur:
                        nom_complet = f"{auteur.prenom or ''} {auteur.nom}".strip()
                        auteurs.append(nom_complet)

                suggestions.extend([livre.titre for livre in livres])
                suggestions.extend(auteurs)
            
            if table_categorie_exists:
                categories = Categorie.objects.filter(nom__icontains=query)[:5]
                suggestions.extend([cat.nom for cat in categories])
                
        except Exception:
            pass

    # Retourner les suggestions uniques
    suggestions = list(set(suggestions))[:10]
    return JsonResponse(suggestions, safe=False)

def autocomplete(request):
    if 'term' in request.GET:
        term = request.GET.get('term')
        try:
            from django.db import connection
            cursor = connection.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bibliotheque_livre'")
            table_livre_exists = cursor.fetchone() is not None
            
            if table_livre_exists:
                livres = Livre.objects.filter(
                    Q(titre__icontains=term) |
                    Q(auteur__icontains=term)
                )
                suggestions = list(livres.values_list('titre', flat=True)[:10])
                return JsonResponse(suggestions, safe=False)
        except Exception:
            pass
    return JsonResponse([], safe=False)

def accueil(request):
    return render(request, 'accueil.html')

def page_accueil(request):
    is_mon_compte_active = request.resolver_match.url_name in ['mon_compte', 'catalogue_categories', 'liste_livres_categorie']
    return render(request, 'accueil.html', {'is_mon_compte_active': is_mon_compte_active})

def presentation_bibliotheque(request):
    return render(request, 'presentation_bibliotheque.html')

@login_requis
def catalogue(request):
    # Vérifier si la table Categorie existe
    try:
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='bibliotheque_categorie'")
        table_categorie_exists = cursor.fetchone() is not None
        
        if table_categorie_exists:
            list_categories = Categorie.objects.all()
        else:
            list_categories = []
    except Exception:
        list_categories = []
    
    est_bibliothecaire = request.utilisateur.est_bibliothecaire if request.utilisateur else False
    
    return render(request, 'index.html', {
        'list_categories': list_categories,
        'est_bibliothecaire': est_bibliothecaire,
        'categories_existent': bool(list_categories),
        'livres_existent': False  # Pas de livres dans cette vue
    })

@login_requis
@require_POST
def ajouter_favori(request, livre_id):
    utilisateur = request.utilisateur
    livre = get_object_or_404(Livre, id=livre_id)
    
    if livre not in utilisateur.favoris.all():
        utilisateur.favoris.add(livre)
        success = True
        message = 'Ajouté'
    else:
        success = False
        message = 'Livre déjà dans les favoris'

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': success, 'message': message})
    
    return redirect('mes_favoris')

@login_requis
def supprimer_favori(request, livre_id):
    utilisateur = request.utilisateur
    livre = get_object_or_404(Livre, id=livre_id)
    utilisateur.favoris.remove(livre)
    messages.success(request, "Livre retiré des favoris !")
    return redirect('mes_favoris')

@login_requis
def mes_favoris(request):
    utilisateur = request.utilisateur
    favoris = utilisateur.favoris.all()
    return render(request, 'mes_favoris.html', {'favoris': favoris})





