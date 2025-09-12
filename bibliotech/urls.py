from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from bibliotheque import views as bibliotheque_views

urlpatterns = [
    path('', bibliotheque_views.accueil, name='accueil'),
    path('bibliotheque/', include('bibliotheque.urls')),
    path('comptes/', include('comptes.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)