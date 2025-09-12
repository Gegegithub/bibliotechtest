from django.urls import path
from . import views


urlpatterns = [
    path('', views.accueil, name='accueil'), 
    path('inscription/', views.inscription, name='inscription'),
    path('connexion/', views.connexion, name='connexion'),
     path('password-reset/', views.password_reset, name='password_reset'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('rendez-vous/', views.rendez_vous, name='rendez_vous'),
    path('confirmation-rdv/', views.confirmation_rdv, name='confirmation_rdv'),
    path('mon-compte/', views.mon_compte, name='mon_compte'),
    path('modifier-informations/', views.modifier_informations, name='modifier_informations'),
    path('changer-mot-de-passe/', views.changer_mot_de_passe, name='changer_mot_de_passe'),
    path('support-contact/', views.support_contact, name='support_contact'),
    path('conditions-generales/', views.conditions_generales, name='conditions_generales'),
    path("rdv/<int:id>/modifier/", views.modifier_rdv, name="modifier_rdv"),
    path('gestion-rendezvous/', views.gestion_rendezvous, name='gestion_rendezvous'),
    path("bibliothecaire/gestion-rdv/", views.gestion_rdv_bibliothecaire, name="gestion_rdv_bibliothecaire"),
    path("notifications/", views.notifications_usager, name="notifications"),
    path('notifier-rdv/<int:rdv_id>/', views.notifier_rdv, name='notifier_rdv'),
    path("notifications/personnel/", views.notifications_personnel, name="notifications_personnel"),
    path("notifications/lire/<int:notif_id>/", views.notification_marquer_lue, name="notification_marquer_lue"),
    path("confirmer-rdv/<int:rendezvous_id>/", views.confirmer_rendezvous, name="confirmer_rdv"),
    path('confirmation-rdv/', views.confirmation_rdv, name='confirmation_rdv'),
    path('mes-rendezvous/', views.mes_rendezvous, name='mes_rendezvous'),
    path('mes_notifications/', views.notifications_usager, name='mes_notifications'),
    path('lire_notification/<int:notification_id>/', views.lire_notification, name='lire_notification'),
    path("dashboard/", views.tableau_de_bord, name="dashboard"),
    path('rapport_pdf/', views.generer_rapport_pdf, name='rapport_pdf'),
    path('administration-utilisateurs/', views.administration_utilisateurs, name='administration_utilisateurs'),
]
