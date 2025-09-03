from django.shortcuts import render, get_object_or_404, redirect
from .models import Categorie, Livre
from comptes.models import ProfilBibliotheque
from django.db.models import Q
from django.http import JsonResponse
from spellchecker import SpellChecker
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.urls import reverse
from django.utils.http import urlencode
from django.views.decorators.http import require_POST
from .forms import CategorieForm, LivreForm 
import wikipedia
wikipedia.set_lang("fr")  # pour le français


spell = SpellChecker(language='fr')  # Correction orthographique simple en français

def home(request):
    list_categories = Categorie.objects.all()
    list_livres = Livre.objects.all()
    est_bibliothecaire = request.user.groups.filter(name='Bibliothécaire').exists()
    return render(request, "index.html", {
        "list_categories": list_categories,
        "list_livres": list_livres,
        "est_bibliothecaire": est_bibliothecaire
    })
    
@permission_required('bibliotheque.add_categorie', raise_exception=True)
def ajouter_categorie(request):
    if request.method == "POST":
        form = CategorieForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('catalogue')  # redirige vers la page catalogue
    else:
        form = CategorieForm()
    return render(request, 'ajouter_categorie.html', {'form': form})

def details_categorie(request, categorie_id):
    categorie = get_object_or_404(Categorie, id=categorie_id)
    livres = Livre.objects.filter(categorie=categorie)
    est_bibliothecaire = request.user.groups.filter(name='Bibliothécaire').exists()
    return render(request, "details.html", {
        "categorie": categorie,
        "livres": livres,
        "est_bibliothecaire": est_bibliothecaire
    })

    
@login_required
@permission_required('bibliotheque.add_livre', raise_exception=True)
def ajouter_livre(request, categorie_id):
    categorie = get_object_or_404(Categorie, pk=categorie_id)
    if request.method == 'POST':
        form = LivreForm(request.POST, request.FILES)
        if form.is_valid():
            livre = form.save(commit=False)
            livre.categorie = categorie
            livre.save()
            return redirect('details_categorie', categorie.id)
    else:
        form = LivreForm()
    return render(request, 'ajouter_livre.html', {'form': form, 'categorie': categorie})


@permission_required('bibliotheque.delete_categorie', raise_exception=True)
def supprimer_categorie(request, categorie_id):
    if request.method == 'POST':
        categorie = get_object_or_404(Categorie, id=categorie_id)
        categorie.delete()
    return redirect('catalogue')  # redirige vers la page catalogue

@permission_required('bibliotheque.change_categorie', raise_exception=True)
def modifier_categorie(request, categorie_id):
    categorie = get_object_or_404(Categorie, id=categorie_id)
    if request.method == 'POST':
        form = CategorieForm(request.POST, request.FILES, instance=categorie)
        if form.is_valid():
            form.save()
            return redirect('catalogue')
    else:
        form = CategorieForm(instance=categorie)
    return render(request, 'modifier_categorie.html', {'form': form, 'categorie': categorie})


@permission_required('bibliotheque.delete_livre', raise_exception=True)
def supprimer_livre(request, livre_id):
    if request.method == 'POST':
        livre = get_object_or_404(Livre, id=livre_id)
        categorie_id = livre.categorie.id  # On garde l'id avant suppression
        livre.delete()
        return redirect('details_categorie', categorie_id=categorie_id)
    return redirect('catalogue')

@login_required
@permission_required('bibliotheque.change_livre', raise_exception=True)
def modifier_livre(request, livre_id):
    livre = get_object_or_404(Livre, id=livre_id)
    
    if request.method == 'POST':
        form = LivreForm(request.POST, request.FILES, instance=livre)
        if form.is_valid():
            form.save()
            return redirect('details_categorie', categorie_id=livre.categorie.id)
    else:
        form = LivreForm(instance=livre)

    return render(request, 'modifier_livre.html', {'form': form, 'livre': livre})


@login_required(login_url='connexion')
def detail_livre(request, categorie_id, livre_id):
    categorie = get_object_or_404(Categorie, id=categorie_id)
    livre = get_object_or_404(Livre, id=livre_id, categorie_id=categorie_id)
    autres_livres = Livre.objects.filter(categorie_id=categorie_id).exclude(id=livre_id)

    profil, _ = ProfilBibliotheque.objects.get_or_create(utilisateur=request.user)
    est_favori = livre in profil.favoris.all()

    description = livre.description or ""  # description en base si dispo

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
        'description': description,  # ⚡ On envoie la description au template
    })

def demander_connexion_detail(request, categorie_id, livre_id):
    messages.warning(request, "Veuillez vous connecter pour consulter ce livre.")
    next_url = reverse('bibliotheque:detail_livre', kwargs={'categorie_id': categorie_id, 'livre_id': livre_id})
    return redirect(f"/comptes/connexion/?next={next_url}")

def recherche(request):
    query = request.GET.get('q', '')
    resultats = Livre.objects.all()
    
    if query:
        resultats = resultats.filter(
            Q(titre__icontains=query) |
            Q(auteur__nom__icontains=query) |
            Q(auteur__prenom__icontains=query) |
            Q(description__icontains=query)
        )

    return render(request, 'recherche_resultats.html', {
        'livres': resultats,
        'query': query
    })
    
def recherche_suggestions(request):
    query = request.GET.get('q', '')
    suggestions = []

    if query:
        livres = Livre.objects.filter(titre__icontains=query)[:5]
        auteurs_livres = Livre.objects.filter(
            Q(auteur__nom__icontains=query) | Q(auteur__prenom__icontains=query)
        )[:5]
        categories = Categorie.objects.filter(nom__icontains=query)[:5]

        auteurs = []
        for livre in auteurs_livres:
            auteur = livre.auteur
            if auteur:
                nom_complet = f"{auteur.prenom or ''} {auteur.nom}".strip()
                auteurs.append(nom_complet)

        suggestions = list(set(
            [livre.titre for livre in livres] +
            auteurs +
            [cat.nom for cat in categories]
        ))[:10]

    return JsonResponse(suggestions, safe=False)

def autocomplete(request):
    if 'term' in request.GET:
        term = request.GET.get('term')
        livres = Livre.objects.filter(
            Q(titre__icontains=term) |
            Q(auteur__icontains=term)
        )
        suggestions = list(livres.values_list('titre', flat=True)[:10])
        return JsonResponse(suggestions, safe=False)
    return JsonResponse([], safe=False)

def accueil(request):
    return render(request, 'accueil.html')

def page_accueil(request):
    is_mon_compte_active = request.resolver_match.url_name in ['mon_compte', 'catalogue_categories', 'liste_livres_categorie']
    return render(request, 'accueil.html', {'is_mon_compte_active': is_mon_compte_active})

def presentation_bibliotheque(request):
    return render(request, 'presentation_bibliotheque.html')

# --- CORRIGÉE : on passe bien les catégories et le flag bibliothécaire ---
def catalogue(request):
    list_categories = Categorie.objects.all()
    est_bibliothecaire = request.user.groups.filter(name='Bibliothécaire').exists()
    return render(request, 'bibliotheque/catalogue.html', {
        'list_categories': list_categories,
        'est_bibliothecaire': est_bibliothecaire
    })

@login_required(login_url='connexion')
@require_POST
def ajouter_favori(request, livre_id):
    profil = get_object_or_404(ProfilBibliotheque, utilisateur=request.user)
    livre = get_object_or_404(Livre, id=livre_id)
    
    if livre not in profil.favoris.all():
        profil.favoris.add(livre)
        success = True
        message = 'Ajouté'
    else:
        success = False
        message = 'Livre déjà dans les favoris'

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'success': success, 'message': message})
    
    return redirect('mes_favoris')

@login_required(login_url='connexion')
def supprimer_favori(request, livre_id):
    profil = get_object_or_404(ProfilBibliotheque, utilisateur=request.user)
    livre = get_object_or_404(Livre, id=livre_id)
    profil.favoris.remove(livre)
    return redirect('mes_favoris')

@login_required(login_url='connexion')
def mes_favoris(request):
    profil = get_object_or_404(ProfilBibliotheque, utilisateur=request.user)
    favoris = profil.favoris.all()
    return render(request, 'mes_favoris.html', {'favoris': favoris})





