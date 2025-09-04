from django.core.management.base import BaseCommand
from comptes.models import Utilisateur


class Command(BaseCommand):
    help = 'Promouvoir ou rétrograder un utilisateur'

    def add_arguments(self, parser):
        parser.add_argument('email', type=str, help='Email de l\'utilisateur')
        parser.add_argument('role', type=str, choices=['admin', 'bibliothecaire', 'personnel', 'utilisateur'], 
                          help='Nouveau rôle de l\'utilisateur')

    def handle(self, *args, **options):
        email = options['email']
        role = options['role']

        try:
            utilisateur = Utilisateur.objects.get(email=email)
            
            # Réinitialiser tous les rôles
            utilisateur.est_admin = False
            utilisateur.est_bibliothecaire = False
            utilisateur.est_personnel = False
            
            # Appliquer le nouveau rôle
            if role == 'admin':
                utilisateur.est_admin = True
                self.stdout.write(
                    self.style.SUCCESS(f'{utilisateur.get_full_name()} a été promu administrateur')
                )
            elif role == 'bibliothecaire':
                utilisateur.est_bibliothecaire = True
                self.stdout.write(
                    self.style.SUCCESS(f'{utilisateur.get_full_name()} a été promu bibliothécaire')
                )
            elif role == 'personnel':
                utilisateur.est_personnel = True
                self.stdout.write(
                    self.style.SUCCESS(f'{utilisateur.get_full_name()} a été promu personnel administratif')
                )
            else:  # utilisateur
                self.stdout.write(
                    self.style.SUCCESS(f'{utilisateur.get_full_name()} a été rétrogradé au statut d\'utilisateur simple')
                )
            
            utilisateur.save()
            
        except Utilisateur.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'Aucun utilisateur trouvé avec l\'email {email}')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Erreur lors de la modification : {str(e)}')
            )
