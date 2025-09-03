from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usager, RendezVous
from django.utils.html import format_html

@admin.register(Usager)
class UsagerAdmin(UserAdmin):
    list_display = ('username', 'email', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets
    add_fieldsets = UserAdmin.add_fieldsets

@admin.register(RendezVous)
class RendezVousAdmin(admin.ModelAdmin):
    list_display = ('id', 'utilisateur', 'date_souhaitee', 'statut', 'contact_utilisateur', 'date_creation')
    list_filter = ('statut', 'date_souhaitee')
    search_fields = ('utilisateur__username', 'utilisateur__email', 'titre_ouvrage')
    ordering = ('-date_souhaitee',)
    list_editable = ('statut',)  # Permet de changer directement le statut dans la liste
    
    def contact_utilisateur(self, obj):
        return format_html('<a href="mailto:{}">Envoyer un email</a>', obj.email)
    contact_utilisateur.short_description = "Contact"

# plus besoin de : admin.site.register(RendezVous, RendezVousAdmin)
