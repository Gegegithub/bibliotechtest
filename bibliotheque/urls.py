from django.urls import path
from . import views

urlpatterns = [
    path('catalogue/', views.home, name='catalogue'),
    path('presentation/', views.presentation_bibliotheque, name='presentation_bibliotheque'),
    path('categorie/<str:categorie_id>/', views.details_categorie, name='details_categorie'),
    path('recherche/', views.recherche, name='recherche'),
]