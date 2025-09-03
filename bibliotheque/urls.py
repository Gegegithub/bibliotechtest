from django.urls import path
from . import views

from django.urls import path
from . import views

urlpatterns = [
    
    path('catalogue/', views.home, name='catalogue'),    # liste livres -> index.html
    path('', views.accueil, name='accueil'),
    path('presentation/', views.presentation_bibliotheque, name='presentation_bibliotheque'),
    path('categorie/<int:categorie_id>/', views.details_categorie, name='details_categorie'),
    path('categorie/ajouter/', views.ajouter_categorie, name='ajouter_categorie'),
    path('categorie/<int:categorie_id>/ajouter_livre/', views.ajouter_livre, name='ajouter_livre'),
    path('supprimer_categorie/<int:categorie_id>/', views.supprimer_categorie, name='supprimer_categorie'),
    path('categorie/modifier/<int:categorie_id>/', views.modifier_categorie, name='modifier_categorie'),
    path('livre/supprimer/<int:livre_id>/', views.supprimer_livre, name='supprimer_livre'),
    path('livre/modifier/<int:livre_id>/', views.modifier_livre, name='modifier_livre'),
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



