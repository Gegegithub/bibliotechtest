# BiblioTECH - Système de Gestion de Bibliothèque

## Configuration

### 1. Cloner le projet
```bash
git clone <votre-repo>
cd bibliotech-test1
```

### 2. Créer un environnement virtuel
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Installer les dépendances
```bash
pip install -r requirements.txt
```

### 4. Configuration des variables d'environnement
Créez un fichier `.env` à la racine du projet avec le contenu suivant :

```env
# Configuration Supabase
SUPABASE_URL=votre_url_supabase
SUPABASE_KEY=votre_cle_anon_supabase
SUPABASE_SERVICE_ROLE_KEY=votre_cle_service_role_supabase

# Configuration Django
SECRET_KEY=votre_secret_key_django
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 5. Configuration de la base de données Supabase
1. Créez un projet sur [supabase.com](https://supabase.com)
2. Exécutez le script SQL dans `init_supabase_tables.sql`
3. Configurez la fonction `handle_new_user()` pour créer automatiquement les profils
4. Mettez à jour les clés dans votre fichier `.env`

### 6. Lancer le serveur
```bash
python manage.py runserver
```

## Structure du projet

- `bibliotheque/` - Application principale de gestion de bibliothèque
- `comptes/` - Application d'authentification avec Supabase
- `bibliotech/` - Configuration Django
- `static/` - Fichiers statiques (CSS, JS, images)
- `templates/` - Templates HTML

## Fonctionnalités

- ✅ Authentification avec Supabase
- ✅ Inscription/Connexion
- ✅ Redirection selon le type d'utilisateur
- ✅ Dashboard pour bibliothécaires
- ✅ Dashboard pour administrateurs
- ✅ Gestion des sessions Django

## Types d'utilisateurs

- **Utilisateur normal** : Accès à l'accueil
- **Bibliothécaire** : Accès au dashboard bibliothécaire
- **Administrateur** : Accès au dashboard administrateur

## Sécurité

⚠️ **IMPORTANT** : Ne jamais commiter le fichier `.env` qui contient vos clés API !

## Développement

Pour le développement, utilisez les variables d'environnement définies dans `.env`.
Pour la production, configurez les variables d'environnement sur votre serveur.
