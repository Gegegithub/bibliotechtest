from django.contrib import admin
from .models import Livre, Categorie, Auteur

class LivreInline(admin.TabularInline):  # ou admin.StackedInline pour un affichage vertical
    model = Livre
    extra = 0  # Nombre de livres vides à afficher par défaut

class CategorieAdmin(admin.ModelAdmin):
    inlines = [LivreInline]
    list_display = ('nom',)
    search_fields = ('nom',)

class LivreAdmin(admin.ModelAdmin):
    list_display = ('titre', 'auteur', 'numero_inventaire', 'categorie', 'date_publication')
    list_filter = ('categorie',)
    search_fields = ('titre', 'auteur', 'numero_inventaire')

admin.site.register(Categorie, CategorieAdmin)
admin.site.register(Livre, LivreAdmin)

class LivreAdmin(admin.ModelAdmin):
    autocomplete_fields = ['auteur']

# Configuration pour l'admin Auteur
@admin.register(Auteur)
class AuteurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'prenom')  # colonnes visibles
    search_fields = ('nom', 'prenom') # permet la recherche



