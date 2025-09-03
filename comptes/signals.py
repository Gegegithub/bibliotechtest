from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.core.mail import send_mail
from .models import RendezVous

@receiver(pre_save, sender=RendezVous)
def notifier_changement_statut(sender, instance, **kwargs):
    if instance.id is None:
        return  # nouveau rendez-vous, on ignore
    ancien_rdv = RendezVous.objects.get(id=instance.id)
    if ancien_rdv.statut != instance.statut:
        send_mail(
            subject=f'Statut de votre rendez-vous: {instance.statut}',
            message=f'Bonjour {instance.nom},\n\nVotre rendez-vous pour "{instance.titre_ouvrage}" est maintenant {instance.statut}.',
            from_email=None,
            recipient_list=[instance.email],
            fail_silently=False,
        )
