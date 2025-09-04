#!/usr/bin/env python
"""
Script de test pour le système d'administration des utilisateurs
"""

import os
import sys
import django

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bibliotech.settings')
django.setup()

from comptes.models import Utilisateur
from django.utils import timezone

def test_admin_system():
    """Test du système d'administration"""
    print("🔍 Test du système d'administration des utilisateurs")
    print("=" * 60)
    
    # 1. Vérifier s'il y a des utilisateurs
    total_users = Utilisateur.objects.count()
    print(f"📊 Total utilisateurs : {total_users}")
    
    if total_users == 0:
        print("❌ Aucun utilisateur trouvé. Créez d'abord un utilisateur.")
        return
    
    # 2. Identifier le premier utilisateur (super admin)
    premier_utilisateur = Utilisateur.objects.order_by('date_inscription').first()
    print(f"👑 Premier utilisateur (Super Admin) : {premier_utilisateur.prenom} {premier_utilisateur.nom}")
    print(f"   Email : {premier_utilisateur.email}")
    print(f"   Date d'inscription : {premier_utilisateur.date_inscription}")
    print(f"   Est admin : {premier_utilisateur.est_admin}")
    print(f"   Est bibliothécaire : {premier_utilisateur.est_bibliothecaire}")
    print(f"   Est personnel : {premier_utilisateur.est_personnel}")
    print(f"   Est actif : {premier_utilisateur.est_actif}")
    
    # 3. Lister tous les utilisateurs avec leurs rôles
    print("\n👥 Liste de tous les utilisateurs :")
    print("-" * 60)
    
    for i, user in enumerate(Utilisateur.objects.all().order_by('date_inscription'), 1):
        roles = []
        if user.est_admin:
            roles.append("Admin")
        if user.est_bibliothecaire:
            roles.append("Bibliothécaire")
        if user.est_personnel:
            roles.append("Personnel")
        if not roles:
            roles.append("Utilisateur")
        
        status = "✅ Actif" if user.est_actif else "❌ Inactif"
        print(f"{i:2d}. {user.prenom} {user.nom:<25} | {user.email:<30} | {', '.join(roles):<20} | {status}")
    
    # 4. Vérifier la logique de super admin
    print(f"\n🔐 Vérification de la logique de super admin :")
    print(f"   Premier utilisateur ID : {premier_utilisateur.id}")
    print(f"   Premier utilisateur est-il admin ? : {premier_utilisateur.est_admin}")
    
    # 5. Statistiques des rôles
    print(f"\n📈 Statistiques des rôles :")
    admins = Utilisateur.objects.filter(est_admin=True).count()
    bibliothecaires = Utilisateur.objects.filter(est_bibliothecaire=True).count()
    personnel = Utilisateur.objects.filter(est_personnel=True).count()
    utilisateurs_simples = total_users - (admins + bibliothecaires + personnel)
    
    print(f"   Administrateurs : {admins}")
    print(f"   Bibliothécaires : {bibliothecaires}")
    print(f"   Personnel : {personnel}")
    print(f"   Utilisateurs simples : {utilisateurs_simples}")
    
    # 6. Test de la méthode save() du modèle
    print(f"\n🧪 Test de la méthode save() du modèle :")
    if premier_utilisateur.est_admin:
        print("   ✅ Le premier utilisateur est bien administrateur")
    else:
        print("   ❌ Le premier utilisateur n'est pas administrateur")
        print("   🔧 Tentative de correction automatique...")
        premier_utilisateur.est_admin = True
        premier_utilisateur.save()
        print("   ✅ Correction appliquée")
    
    print("\n" + "=" * 60)
    print("🎉 Test terminé !")
    
    # 7. Instructions d'utilisation
    print(f"\n📖 Instructions d'utilisation :")
    print(f"   1. Connectez-vous avec : {premier_utilisateur.email}")
    print(f"   2. Allez dans 'Mon Compte'")
    print(f"   3. Cliquez sur 'Administration des Utilisateurs'")
    print(f"   4. Gérez les rôles des autres utilisateurs")
    
    print(f"\n💻 Commandes disponibles :")
    print(f"   python manage.py promouvoir_utilisateur <email> admin")
    print(f"   python manage.py promouvoir_utilisateur <email> bibliothecaire")
    print(f"   python manage.py promouvoir_utilisateur <email> personnel")
    print(f"   python manage.py promouvoir_utilisateur <email> utilisateur")

if __name__ == "__main__":
    try:
        test_admin_system()
    except Exception as e:
        print(f"❌ Erreur lors du test : {str(e)}")
        import traceback
        traceback.print_exc()
