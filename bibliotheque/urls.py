from django.urls import path
from . import views

from django.urls import path
from . import views

urlpatterns = [
    
    path('catalogue/', views.home, name='catalogue'),    # liste livres -> index.html
    path('', views.accueil, name='accueil'),
    path('presentation/', views.presentation_bibliotheque, name='presentation_bibliotheque'),
    path('categorie/<int:categorie_id>/', views.details_categorie, name='details_categorie'),
    path('livre/<int:livre_id>/', views.detail_livre, name='detail_livre'),
    path('categorie/<int:categorie_id>/livre/<int:livre_id>/', views.detail_livre, name='detail_livre'),
    path('categorie/<int:categorie_id>/livre/<int:livre_id>/demander-connexion/', views.demander_connexion_detail, name='demander_connexion_detail'),
    path('recherche/', views.recherche, name='recherche'),
    path('recherche_suggestions/', views.recherche_suggestions, name='recherche_suggestions'),
    path('autocomplete/', views.autocomplete, name='autocomplete'),
    path('ajouter_favori/<int:livre_id>/', views.ajouter_favori, name='ajouter_favori'),
    path('mes_favoris/', views.mes_favoris, name='mes_favoris'),
    path('supprimer_favori/<int:livre_id>/', views.supprimer_favori, name='supprimer_favori'),
]



