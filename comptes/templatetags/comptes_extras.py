from django import template
from django.db.models import Min
from comptes.models import Utilisateur

register = template.Library()

@register.filter
def first_utilisateur_id(value):
    """
    Retourne l'ID du premier utilisateur inscrit
    """
    premier = Utilisateur.objects.order_by('date_inscription').first()
    return premier.id if premier else None

@register.filter
def is_super_admin(utilisateur):
    """
    Vérifie si l'utilisateur est le super administrateur (premier inscrit)
    """
    premier = Utilisateur.objects.order_by('date_inscription').first()
    return premier and utilisateur.id == premier.id
