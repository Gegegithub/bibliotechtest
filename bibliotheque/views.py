from django.shortcuts import render, get_object_or_404, redirect
from .models import Categorie, Livre
from comptes.models import ProfilBibliotheque
from django.db.models import Q
from django.http import JsonResponse
from spellchecker import SpellChecker
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.utils.http import urlencode
from django.views.decorators.http import require_POST
from django.http import JsonResponse



spell = SpellChecker(language='fr')  # Correction orthographique simple en français

def home(request):
    list_categories = Categorie.objects.all()
    list_livres = Livre.objects.all()
    return render(request, "index.html", {
        "list_categories": list_categories,
        "list_livres": list_livres
    })

def details_categorie(request, categorie_id):
    categorie = get_object_or_404(Categorie, id=categorie_id)
    livres = Livre.objects.filter(categorie=categorie)
    return render(request, "details.html", {
        "categorie": categorie,
        "livres": livres
    })

@login_required(login_url='connexion')
def detail_livre(request, categorie_id, livre_id):
    categorie = get_object_or_404(Categorie, id=categorie_id)
    livre = get_object_or_404(Livre, id=livre_id, categorie_id=categorie_id)
    autres_livres = Livre.objects.filter(categorie_id=categorie_id).exclude(id=livre_id)

    # Récupérer ou créer le profil automatiquement si l'utilisateur n'en a pas
    profil, _ = ProfilBibliotheque.objects.get_or_create(utilisateur=request.user)

    est_favori = livre in profil.favoris.all()

    # Gestion AJAX pour ajouter aux favoris
    if request.method == 'POST' and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        if not est_favori:
            profil.favoris.add(livre)
            profil.save()
            return JsonResponse({'success': True})
        else:
            return JsonResponse({'success': False, 'error': 'Livre déjà en favoris'}, status=400)

    # Construction de l'URL Wikipédia de l'auteur
    if livre.auteur:
        author_name = f"{livre.auteur.prenom or ''} {livre.auteur.nom}".strip()
        wiki_url = f"https://fr.wikipedia.org/wiki/{author_name.replace(' ', '_')}"
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

def catalogue(request):
    return render(request, 'bibliotheque/catalogue.html')


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
    return redirect('mes_favoris')  # Redirige vers la page des favoris après suppression


@login_required(login_url='connexion')
def mes_favoris(request):
    profil = get_object_or_404(ProfilBibliotheque, utilisateur=request.user)
    favoris = profil.favoris.all()
    return render(request, 'mes_favoris.html', {'favoris': favoris})



