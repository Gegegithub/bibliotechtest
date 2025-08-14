from django.urls import path
from django.contrib.auth import views as auth_views
from . import views
from .views import Connexion

urlpatterns = [
    path('', views.accueil, name='accueil'), 
    path('inscription/', views.inscription, name='inscription'),
    path('inscription2/', views.inscription2, name='inscription2'),
    path('connexion/', auth_views.LoginView.as_view(template_name='connexion.html'), name='connexion.html'),
    path('connexion/', views.connexion, name='connexion'),
    path('password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
    path('logout/', auth_views.LogoutView.as_view(), name='deconnexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('rendez-vous/', views.rendez_vous, name='rendez_vous'),
    path('confirmation-rdv/', views.confirmation_rdv, name='confirmation_rdv'),
    path('mon-compte/', views.mon_compte, name='mon_compte'),
    path('modifier-informations/', views.modifier_informations, name='modifier_informations'),
    path('changer-mot-de-passe/', views.changer_mot_de_passe, name='changer_mot_de_passe'),
    path('support-contact/', views.support_contact, name='support_contact'),
    path('conditions-generales/', views.conditions_generales, name='conditions_generales'),
]