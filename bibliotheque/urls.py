from django.urls import path
from . import views

urlpatterns = [
    path('catalogue/', views.home, name='catalogue'),
    path('presentation/', views.presentation_bibliotheque, name='presentation_bibliotheque'),
    path('categorie/<str:categorie_id>/', views.details_categorie, name='details_categorie'),
    path('categorie/<str:categorie_id>/livre/<str:livre_id>/', views.detail_livre, name='detail_livre'),
    path('categorie/<str:categorie_id>/livre/<str:livre_id>/connexion/', views.demander_connexion_detail, name='demander_connexion_detail'),
    path('ajouter-favori/<str:livre_id>/', views.ajouter_favori, name='ajouter_favori'),
    path('supprimer-favori/<str:livre_id>/', views.supprimer_favori, name='supprimer_favori'),
    path('ajouter-categorie/', views.ajouter_categorie, name='ajouter_categorie'),
    path('modifier-categorie/<str:categorie_id>/', views.modifier_categorie, name='modifier_categorie'),
    path('supprimer-categorie/<str:categorie_id>/', views.supprimer_categorie, name='supprimer_categorie'),
    path('ajouter-livre/<str:categorie_id>/', views.ajouter_livre, name='ajouter_livre'),
    path('modifier-livre/<str:livre_id>/', views.modifier_livre, name='modifier_livre'),
    path('supprimer-livre/<str:livre_id>/', views.supprimer_livre, name='supprimer_livre'),
    path('mes-favoris/', views.mes_favoris, name='mes_favoris'),
    path('recherche/', views.recherche, name='recherche'),
    path('recherche-suggestions/', views.recherche_suggestions, name='recherche_suggestions'),
    path('autocomplete/', views.autocomplete, name='autocomplete'),
]