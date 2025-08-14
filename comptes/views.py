from django.shortcuts import render, redirect, get_object_or_404, redirect
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import Etape2ProfilForm, ProfilBibliotheque
from django.contrib.auth.views import LoginView
from .forms import RendezVousForm
from comptes.models import Usager



def inscription(request):
    if request.method == "POST":
        nom = request.POST.get('nom')
        prenom = request.POST.get('prenom')
        email = request.POST.get('email')
        password1 = request.POST.get('password1')
        password2 = request.POST.get('password2')

        if password1 == password2:
            if Usager.objects.filter(username=email).exists():
                messages.error(request, "Un compte avec cet email existe déjà.")
                return redirect('inscription')
            user = Usager.objects.create_user(
                username=email,
                email=email,
                password=password1,
                first_name=prenom,
                last_name=nom
            )
            login(request, user)
            messages.success(request, "Inscription réussie. Complétez maintenant votre profil.")
            return redirect('inscription2')
        else:
            messages.error(request, "Les mots de passe ne correspondent pas.")
            return redirect('inscription')
    return render(request, 'inscription.html')


@login_required
def inscription2(request):
    utilisateur = request.user

    try:
        profil = ProfilBibliotheque.objects.get(utilisateur=utilisateur)
    except ProfilBibliotheque.DoesNotExist:
        profil = ProfilBibliotheque(utilisateur=utilisateur)

    if request.method == 'POST':
        form = Etape2ProfilForm(request.POST, request.FILES, instance=profil)
        if form.is_valid():
            form.save()
            messages.success(request, "Profil complété avec succès. Vous pouvez maintenant vous connecter.")
            return redirect('connexion')
        else:
            messages.error(request, "Veuillez corriger les erreurs du formulaire.")
    else:
        form = Etape2ProfilForm(instance=profil)

    return render(request, 'inscription2.html', {'form': form})


def connexion(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Vous êtes bien connecté(e) !")

            # Récupérer le paramètre next en POST ou GET
            next_url = request.POST.get('next') or request.GET.get('next')

            if next_url:
                return redirect(next_url)
            else:
                return redirect('accueil')
        else:
            messages.error(request, "Email ou mot de passe invalide.")
    else:
        form = AuthenticationForm()

    # Transmettre next dans le template (depuis GET)
    next_url = request.GET.get('next', '')

    return render(request, 'connexion.html', {'form': form, 'next': next_url})


def Connexion (request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            next_url = request.POST.get('next') or request.GET.get('next')
            return redirect(next_url if next_url else 'accueil')
        else:
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")

    next_url = request.GET.get('next', '')
    return render(request, 'connexion.html', {'next': next_url})


def deconnexion(request):
    logout(request)
    messages.info(request, "Vous avez été déconnecté(e).")
    return redirect('accueil')

@login_required(login_url='connexion')
def rendez_vous(request):
    if request.method == 'POST':
        form = RendezVousForm(request.POST)
        if form.is_valid():
            rdv = form.save(commit=False)

            # Ici on met directement l'utilisateur (Usager)
            rdv.utilisateur = request.user  

            rdv.save()
            return redirect('confirmation_rdv')
    else:
        form = RendezVousForm()

    return render(request, 'rendez_vous.html', {'form': form})


def confirmation_rdv(request):
    return render(request, 'confirmation_rdv.html')

def accueil(request):
    return render(request, 'accueil.html')


@login_required(login_url='connexion')
def mon_compte(request):
    user = request.user
    # récupère éventuellement d'autres infos liées au user
    return render(request, 'mon_compte.html', {'user': user})

def modifier_informations(request):
    # Logique pour modifier les infos utilisateur
    return render(request, 'modifier_informations.html')

def changer_mot_de_passe(request):
    # Logique pour afficher et gérer le formulaire de changement de mot de passe
    return render(request, 'changer_mot_de_passe.html')

def support_contact(request):
    # Logique ou affichage simple
    return render(request, 'support_contact.html')

def conditions_generales(request):
    # Logique ou affichage simple
    return render(request, 'conditions_generales.html')








