# 📚 Bibliotech - Système de Gestion de Bibliothèque

## 🎯 Vue d'Ensemble

Bibliotech est une plateforme de gestion intelligente de bibliothèque développée pour la Chambre de Commerce, d'Industrie et de Services de Casablanca-Settat. Le système utilise une authentification personnalisée avec un système de rôles et permissions sophistiqué.

## 🔐 Système d'Authentification Personnalisé

### Modèle Utilisateur (`comptes/models.py`)

Le système utilise un modèle `Utilisateur` personnalisé au lieu du système Django standard :

```python
class Utilisateur(models.Model):
    # Champs d'identification
    email = models.EmailField(unique=True, verbose_name="Adresse email")
    mot_de_passe = models.CharField(max_length=128, verbose_name="Mot de passe")
    prenom = models.CharField(max_length=100, verbose_name="Prénom")
    nom = models.CharField(max_length=100, verbose_name="Nom")
    
    # Rôles et permissions (champs booléens)
    est_admin = models.BooleanField(default=False, verbose_name="Est administrateur")
    est_bibliothecaire = models.BooleanField(default=False, verbose_name="Est bibliothécaire")
    est_personnel = models.BooleanField(default=False, verbose_name="Est personnel administratif")
    est_actif = models.BooleanField(default=True, verbose_name="Compte actif")
    
    # Métadonnées
    date_inscription = models.DateTimeField(auto_now_add=True, verbose_name="Date d'inscription")
    derniere_connexion = models.DateTimeField(null=True, blank=True, verbose_name="Dernière connexion")
    
    # Relations
    favoris = models.ManyToManyField('bibliotheque.Livre', blank=True, verbose_name="Livres favoris")
    
    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.email})"
    
    def save(self, *args, **kwargs):
        # 🎯 LOGIQUE CLÉ : Premier inscrit = Super Admin automatiquement
        if not Utilisateur.objects.exists():
            self.est_admin = True
            self.est_actif = True
        super().save(*args, **kwargs)
```

## 🏆 Hiérarchie des Rôles et Permissions

### Niveaux de Permissions (du plus élevé au plus bas)

#### 1. 🥇 Super Administrateur (`est_admin = True`)
- **Premier utilisateur inscrit** automatiquement
- **Gestion complète** de tous les utilisateurs
- **Promotion/rétrogradation** des rôles
- **Accès à toutes** les fonctionnalités

#### 2. 🔵 Bibliothécaire (`est_bibliothecaire = True`)
- **Gestion des livres** et catégories
- **Gestion des rendez-vous**
- **Accès aux notifications** bibliothécaire

#### 3. 🟡 Personnel Administratif (`est_personnel = True`)
- **Gestion administrative** des rendez-vous
- **Support utilisateur**
- **Accès aux notifications** personnel

#### 4. 🟢 Lecteur (aucun rôle spécial)
- **Consultation du catalogue**
- **Gestion de ses favoris**
- **Prise de rendez-vous**
- **Accès à ses notifications**

## 🛡️ Système de Décorateurs de Permissions

### Décorateur `@login_requis` (`comptes/middleware.py`)

```python
def login_requis(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.utilisateur:
            messages.error(request, "Vous devez être connecté pour accéder à cette page.")
            return redirect('connexion')
        return view_func(request, *args, **kwargs)
    return wrapper
```

**Fonction :** Vérifie que l'utilisateur est connecté
**Utilisation :** `@login_requis` sur les vues nécessitant une connexion

### Décorateur `@permission_requise` (`comptes/middleware.py`)

```python
def permission_requise(permission_type):
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.utilisateur:
                messages.error(request, "Vous devez être connecté pour accéder à cette page.")
                return redirect('connexion')
            
            if permission_type == 'bibliothecaire' and not request.utilisateur.est_bibliothecaire:
                messages.error(request, "Vous devez être bibliothécaire pour accéder à cette page.")
                return redirect('accueil')
            
            if permission_type == 'admin' and not request.utilisateur.est_admin:
                messages.error(request, "Vous devez être administrateur pour accéder à cette page.")
                return redirect('accueil')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
```

**Fonction :** Vérifie le rôle spécifique requis
**Utilisation :** `@permission_requise('bibliothecaire')` ou `@permission_requise('admin')`

## 🔄 Middleware d'Authentification

### `AuthentificationMiddleware` (`comptes/middleware.py`)

```python
class AuthentificationMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        utilisateur_id = request.session.get('utilateur_id')
        if utilisateur_id:
            try:
                request.utilisateur = Utilisateur.objects.get(id=utilisateur_id)
            except Utilisateur.DoesNotExist:
                del request.session['utilisateur_id']
                request.utilisateur = None
        else:
            request.utilisateur = None

        response = self.get_response(request)
        return response
```

**Fonction :** 
- Récupère l'utilisateur depuis la session
- Attache `request.utilisateur` à chaque requête
- Gère les sessions expirées

## 👑 Système d'Administration des Utilisateurs

### Vue d'Administration (`comptes/views.py`)

```python
@login_requis
def administration_utilisateurs(request):
    """
    Vue d'administration des utilisateurs - accessible uniquement au premier utilisateur (super admin)
    """
    # 🔒 Vérification : Seul le premier utilisateur peut accéder
    premier_utilisateur = Utilisateur.objects.order_by('date_inscription').first()
    
    if not premier_utilisateur or request.utilisateur.id != premier_utilisateur.id:
        messages.error(request, "Accès refusé : cette fonctionnalité est réservée au super administrateur.")
        return redirect('accueil')
    
    if request.method == 'POST':
        action = request.POST.get('action')
        utilisateur_id = request.POST.get('utilisateur_id')
        
        try:
            utilisateur_cible = Utilisateur.objects.get(id=utilisateur_id)
            
            if action == 'promouvoir_lecteur':
                # 📖 Lecteur = utilisateur simple (aucun rôle spécial)
                utilisateur_cible.est_admin = False
                utilisateur_cible.est_bibliothecaire = False
                utilisateur_cible.est_personnel = False
                messages.success(request, f"{utilisateur_cible.prenom} {utilisateur_cible.nom} a été promu lecteur.")
                
            elif action == 'promouvoir_bibliothecaire':
                # 🔵 Bibliothécaire = gestion des livres et RDV
                utilisateur_cible.est_bibliothecaire = True
                utilisateur_cible.est_admin = False
                utilisateur_cible.est_personnel = False
                messages.success(request, f"{utilisateur_cible.prenom} {utilisateur_cible.nom} a été promu bibliothécaire.")
                
            elif action == 'promouvoir_personnel':
                # 🟡 Personnel = gestion administrative et RDV
                utilisateur_cible.est_personnel = True
                utilisateur_cible.est_admin = False
                utilisateur_cible.est_bibliothecaire = False
                messages.success(request, f"{utilisateur_cible.prenom} {utilisateur_cible.nom} a été promu personnel administratif.")
                
            elif action == 'activer_compte':
                utilisateur_cible.est_actif = True
                messages.success(request, f"Le compte de {utilisateur_cible.prenom} {utilisateur_cible.nom} a été activé.")
                
            elif action == 'desactiver_compte':
                utilisateur_cible.est_actif = False
                messages.success(request, f"Le compte de {utilisateur_cible.prenom} {utilisateur_cible.nom} a été désactivé.")
            
            utilisateur_cible.save()
            
        except Utilisateur.DoesNotExist:
            messages.error(request, "Utilisateur introuvable.")
        except Exception as e:
            messages.error(request, f"Erreur lors de la modification : {str(e)}")
    
    # Récupérer tous les utilisateurs sauf le super admin
    utilisateurs = Utilisateur.objects.exclude(id=premier_utilisateur.id).order_by('-date_inscription')
    
    context = {
        'utilisateurs': utilisateurs,
        'premier_utilisateur': premier_utilisateur,
    }
    
    return render(request, 'administration_utilisateurs.html', context)
```

## 📋 Exemples d'Utilisation dans les Vues

### Vue Réservée aux Bibliothécaires

```python
@login_requis
@permission_requise('bibliothecaire')
def ajouter_categorie(request):
    # 🔒 Seuls les bibliothécaires connectés peuvent accéder
    if request.method == "POST":
        form = CategorieForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Catégorie ajoutée avec succès !")
            return redirect('catalogue')
    else:
        form = CategorieForm()
    return render(request, 'ajouter_categorie.html', {'form': form})
```

### Vue Réservée aux Administrateurs

```python
@login_requis
@permission_requise('admin')
def gestion_rendezvous(request):
    # 🔒 Seuls les super admins peuvent accéder
    rdvs = RendezVous.objects.all().order_by('date_souhaitee')
    
    # Initialiser les groupes par statut
    groupes = {
        'En attente': [],
        'Confirmés': [],
        'Terminés': [],
        'Annulés': [],
    }
    
    # ... logique de gestion des RDV ...
    
    return render(request, 'gestion_rendezvous.html', {'groupes': groupes})
```

### Vue Accessible à Tous les Utilisateurs Connectés

```python
@login_requis
def mes_favoris(request):
    # 🔓 Tous les utilisateurs connectés peuvent accéder
    utilisateur = request.utilisateur
    favoris = utilisateur.favoris.all()
    return render(request, 'mes_favoris.html', {'favoris': favoris})
```

## 🎨 Gestion des Permissions dans les Templates

### Vérification de Connexion

```html
{% if request.utilisateur %}
    <!-- Contenu visible uniquement pour les utilisateurs connectés -->
    <li class="nav-item dropdown">
        <a class="nav-link dropdown-toggle" href="#" id="monCompteDropdown" role="button"
           data-bs-toggle="dropdown" aria-expanded="false">
            Mon Compte
        </a>
        <ul class="dropdown-menu dropdown-menu-center">
            <li><a class="dropdown-item" href="{% url 'mon_compte' %}">
                <i class="bi bi-person-circle me-2"></i>Profil
            </a></li>
            <li><a class="dropdown-item" href="{% url 'mes_favoris' %}">
                <i class="bi bi-heart me-2"></i>Mes favoris
            </a></li>
        </ul>
    </li>
{% else %}
    <!-- Contenu visible pour les visiteurs non connectés -->
    <li class="nav-item">
        <a class="nav-link" href="{% url 'connexion' %}">Se connecter</a>
    </li>
{% endif %}
```

### Vérification des Rôles

```html
{% if request.utilisateur.est_bibliothecaire %}
    <!-- Boutons de gestion visibles uniquement pour les bibliothécaires -->
    <div class="text-end mb-3">
        <a href="{% url 'ajouter_categorie' %}" class="btn">
            <i class="bi bi-plus-circle me-2"></i>Ajouter une catégorie
        </a>
    </div>
{% endif %}

{% if request.utilisateur.est_admin %}
    <!-- Fonctionnalités réservées aux administrateurs -->
    <div class="text-end mb-3">
        <a href="{% url 'administration_utilisateurs' %}" class="btn btn-warning">
            <i class="bi bi-people me-2"></i>Administration des Utilisateurs
        </a>
    </div>
{% endif %}
```

## 🔒 Sécurité et Contrôle d'Accès

### Double Protection
- **Frontend** : Templates conditionnels (`{% if %}`)
- **Backend** : Décorateurs de permissions (`@permission_requise`)

### Redirection Automatique
- Utilisateurs non connectés → `connexion`
- Utilisateurs sans permission → `accueil`

### Messages d'Erreur Contextuels
```python
# Dans les vues
messages.error(request, "Vous devez être connecté pour accéder à cette page.")
messages.error(request, "Vous devez être bibliothécaire pour accéder à cette page.")
messages.error(request, "Accès refusé : réservé au super administrateur.")
```

## 🚀 Avantages de ce Système

1. **Flexibilité** : Rôles multiples possibles par utilisateur
2. **Sécurité** : Vérifications côté serveur et client
3. **Maintenabilité** : Logique centralisée dans les décorateurs
4. **Évolutivité** : Facile d'ajouter de nouveaux rôles
5. **Cohérence** : Même logique partout dans l'application

## 💡 Exemple de Flux Complet

### 1. Inscription du Premier Utilisateur
```python
# L'utilisateur s'inscrit via le formulaire
utilisateur = InscriptionForm(request.POST, request.FILES).save()

# La méthode save() est automatiquement appelée
# if not Utilisateur.objects.exists():  # True (premier utilisateur)
#     self.est_admin = True             # Devient super admin
#     self.est_actif = True             # Compte activé

# L'utilisateur est maintenant super administrateur !
```

### 2. Connexion et Session
```python
# L'utilisateur se connecte
if utilisateur.check_password(mot_de_passe):
    request.session['utilisateur_id'] = utilisateur.id
    # Middleware attache request.utilisateur automatiquement
```

### 3. Vérification des Permissions
```python
# L'utilisateur accède à une vue protégée
@login_requis                    # ✅ Connecté
@permission_requise('admin')     # ✅ Est admin
def administration_utilisateurs(request):
    # Vue exécutée avec succès
```

### 4. Affichage Conditionnel
```html
<!-- Dans le template -->
{% if request.utilisateur.est_admin %}
    <!-- Interface d'administration visible -->
{% endif %}
```

## 🎯 Points Clés à Retenir

1. **Premier inscrit = Super Admin automatiquement** (méthode `save()`)
2. **Décorateurs** : `@login_requis` et `@permission_requise`
3. **Middleware** : Attache `request.utilisateur` à chaque requête
4. **Double protection** : Backend (décorateurs) + Frontend (templates)
5. **Promotions** : Seul le super admin peut promouvoir/rétrograder
6. **Sécurité** : Redirections automatiques pour les accès non autorisés

**Cette architecture garantit une gestion sécurisée et cohérente des permissions dans toute l'application Bibliotech !** 🎉
