from django.urls import path
from . import views

urlpatterns = [
    path('inscription/', views.inscription, name='inscription'),
    path('connexion/', views.connexion, name='connexion'),
    path('deconnexion/', views.deconnexion, name='deconnexion'),
    path('mon-compte/', views.mon_compte, name='mon_compte'),
    path('dashboard-bibliothecaire/', views.dashboard_bibliothecaire, name='dashboard_bibliothecaire'),
    path('dashboard-admin/', views.dashboard_admin, name='dashboard_admin'),
]