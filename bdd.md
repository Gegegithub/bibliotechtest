# 🗄️ Base de Données Bibliotech - Scripts SQL

## 📋 Vue d'Ensemble

Ce document contient tous les scripts SQL nécessaires pour créer la base de données Bibliotech depuis zéro. Les tables sont organisées par application et incluent toutes les contraintes, clés étrangères et relations.

## 🔧 Tables Système Django

### **1. `django_migrations`**
```sql
CREATE TABLE django_migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    app VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    applied DATETIME NOT NULL
);
```

### **2. `django_content_type`**
```sql
CREATE TABLE django_content_type (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    app_label VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    UNIQUE(app_label, model)
);
```

### **3. `django_session`**
```sql
CREATE TABLE django_session (
    session_key VARCHAR(40) PRIMARY KEY,
    session_data TEXT NOT NULL,
    expire_date DATETIME NOT NULL
);
```

## 📚 Tables Application `bibliotheque`

### **4. `bibliotheque_auteur`**
```sql
CREATE TABLE bibliotheque_auteur (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NULL,
    CONSTRAINT bibliotheque_auteur_nom_prenom_unique UNIQUE(nom, prenom)
);

-- Index pour optimiser les recherches
CREATE INDEX idx_bibliotheque_auteur_nom ON bibliotheque_auteur(nom);
CREATE INDEX idx_bibliotheque_auteur_prenom ON bibliotheque_auteur(prenom);
```

### **5. `bibliotheque_categorie`**
```sql
CREATE TABLE bibliotheque_categorie (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom VARCHAR(100) NOT NULL UNIQUE,
    image VARCHAR(255) NULL
);

-- Index pour optimiser les recherches
CREATE INDEX idx_bibliotheque_categorie_nom ON bibliotheque_categorie(nom);
```

### **6. `bibliotheque_livre`**
```sql
CREATE TABLE bibliotheque_livre (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre VARCHAR(200) NOT NULL,
    auteur_id INTEGER NULL,
    description TEXT NULL,
    image VARCHAR(255) NULL,
    numero_inventaire VARCHAR(50) NOT NULL UNIQUE,
    ancien_code VARCHAR(50) NULL,
    date_publication DATE NOT NULL,
    categorie_id INTEGER NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Contraintes de clés étrangères
    FOREIGN KEY (auteur_id) REFERENCES bibliotheque_auteur(id) ON DELETE SET NULL,
    FOREIGN KEY (categorie_id) REFERENCES bibliotheque_categorie(id) ON DELETE SET NULL,
    
    -- Contraintes de validation
    CONSTRAINT bibliotheque_livre_titre_not_empty CHECK (length(trim(titre)) > 0),
    CONSTRAINT bibliotheque_livre_numero_inventaire_not_empty CHECK (length(trim(numero_inventaire)) > 0)
);

-- Index pour optimiser les performances
CREATE INDEX idx_bibliotheque_livre_titre ON bibliotheque_livre(titre);
CREATE INDEX idx_bibliotheque_livre_auteur_id ON bibliotheque_livre(auteur_id);
CREATE INDEX idx_bibliotheque_livre_categorie_id ON bibliotheque_livre(categorie_id);
CREATE INDEX idx_bibliotheque_livre_numero_inventaire ON bibliotheque_livre(numero_inventaire);
CREATE INDEX idx_bibliotheque_livre_date_publication ON bibliotheque_livre(date_publication);
```

## 👥 Tables Application `comptes`

### **7. `comptes_utilisateur`**
```sql
CREATE TABLE comptes_utilisateur (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(254) NOT NULL UNIQUE,
    mot_de_passe VARCHAR(128) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    nom VARCHAR(100) NOT NULL,
    type_utilisateur VARCHAR(20) NOT NULL CHECK (type_utilisateur IN ('etudiant', 'professionnel', 'membre_entreprise')),
    profession VARCHAR(100) NULL,
    institution VARCHAR(100) NULL,
    secteur_activite VARCHAR(100) NULL,
    adresse TEXT NULL,
    telephone VARCHAR(20) NULL,
    photo VARCHAR(255) NULL,
    date_inscription DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    derniere_connexion DATETIME NULL,
    est_actif BOOLEAN NOT NULL DEFAULT 1,
    est_admin BOOLEAN NOT NULL DEFAULT 0,
    est_bibliothecaire BOOLEAN NOT NULL DEFAULT 0,
    est_personnel BOOLEAN NOT NULL DEFAULT 0,
    
    -- Contraintes de validation
    CONSTRAINT comptes_utilisateur_email_valid CHECK (email LIKE '%_@_%'),
    CONSTRAINT comptes_utilisateur_prenom_not_empty CHECK (length(trim(prenom)) > 0),
    CONSTRAINT comptes_utilisateur_nom_not_empty CHECK (length(trim(nom)) > 0),
    CONSTRAINT comptes_utilisateur_telephone_format CHECK (telephone IS NULL OR length(telephone) >= 8)
);

-- Index pour optimiser les performances
CREATE INDEX idx_comptes_utilisateur_email ON comptes_utilisateur(email);
CREATE INDEX idx_comptes_utilisateur_nom_prenom ON comptes_utilisateur(nom, prenom);
CREATE INDEX idx_comptes_utilisateur_type_utilisateur ON comptes_utilisateur(type_utilisateur);
CREATE INDEX idx_comptes_utilisateur_est_actif ON comptes_utilisateur(est_actif);
CREATE INDEX idx_comptes_utilisateur_est_admin ON comptes_utilisateur(est_admin);
CREATE INDEX idx_comptes_utilisateur_est_bibliothecaire ON comptes_utilisateur(est_bibliothecaire);
CREATE INDEX idx_comptes_utilisateur_est_personnel ON comptes_utilisateur(est_personnel);
CREATE INDEX idx_comptes_utilisateur_date_inscription ON comptes_utilisateur(date_inscription);
```

### **8. `comptes_rendezvous`**
```sql
CREATE TABLE comptes_rendezvous (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utilisateur_id INTEGER NOT NULL,
    statut VARCHAR(20) NOT NULL DEFAULT 'en_attente' CHECK (statut IN ('en_attente', 'confirme', 'annule', 'termine')),
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    telephone VARCHAR(20) NOT NULL,
    email VARCHAR(254) NOT NULL,
    type_utilisateur VARCHAR(50) NOT NULL CHECK (type_utilisateur IN ('etudiant_chercheur', 'professeur_chercheur', 'academique', 'professionnel', 'porteur_projet', 'autre')),
    titre_ouvrage VARCHAR(200) NULL,
    auteur_ouvrage VARCHAR(200) NULL,
    numero_inventaire VARCHAR(100) NULL,
    ancien_code VARCHAR(100) NULL,
    raison TEXT NOT NULL,
    date_souhaitee DATE NOT NULL,
    message TEXT NULL,
    date_creation DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    heure_entree TIME NULL,
    heure_sortie TIME NULL,
    livre_id INTEGER NOT NULL,
    
    -- Contraintes de clés étrangères
    FOREIGN KEY (utilisateur_id) REFERENCES comptes_utilisateur(id) ON DELETE CASCADE,
    FOREIGN KEY (livre_id) REFERENCES bibliotheque_livre(id) ON DELETE CASCADE,
    
    -- Contraintes de validation
    CONSTRAINT comptes_rendezvous_nom_not_empty CHECK (length(trim(nom)) > 0),
    CONSTRAINT comptes_rendezvous_prenom_not_empty CHECK (length(trim(prenom)) > 0),
    CONSTRAINT comptes_rendezvous_raison_not_empty CHECK (length(trim(raison)) > 0),
    CONSTRAINT comptes_rendezvous_date_souhaitee_future CHECK (date_souhaitee >= date('now')),
    CONSTRAINT comptes_rendezvous_heure_coherence CHECK (
        (heure_entree IS NULL AND heure_sortie IS NULL) OR
        (heure_entree IS NOT NULL AND heure_sortie IS NOT NULL AND heure_entree < heure_sortie)
    )
);

-- Index pour optimiser les performances
CREATE INDEX idx_comptes_rendezvous_utilisateur_id ON comptes_rendezvous(utilisateur_id);
CREATE INDEX idx_comptes_rendezvous_livre_id ON comptes_rendezvous(livre_id);
CREATE INDEX idx_comptes_rendezvous_statut ON comptes_rendezvous(statut);
CREATE INDEX idx_comptes_rendezvous_date_souhaitee ON comptes_rendezvous(date_souhaitee);
CREATE INDEX idx_comptes_rendezvous_date_creation ON comptes_rendezvous(date_creation);
CREATE INDEX idx_comptes_rendezvous_nom_prenom ON comptes_rendezvous(nom, prenom);
```

### **9. `comptes_notification`**
```sql
CREATE TABLE comptes_notification (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utilisateur_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    url VARCHAR(255) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    lu BOOLEAN NOT NULL DEFAULT 0,
    
    -- Contraintes de clés étrangères
    FOREIGN KEY (utilisateur_id) REFERENCES comptes_utilisateur(id) ON DELETE CASCADE,
    
    -- Contraintes de validation
    CONSTRAINT comptes_notification_message_not_empty CHECK (length(trim(message)) > 0)
);

-- Index pour optimiser les performances
CREATE INDEX idx_comptes_notification_utilisateur_id ON comptes_notification(utilisateur_id);
CREATE INDEX idx_comptes_notification_created_at ON comptes_notification(created_at);
CREATE INDEX idx_comptes_notification_lu ON comptes_notification(lu);
```

## 🔗 Tables de Liaison (Relations Many-to-Many)

### **10. `comptes_utilisateur_favoris`**
```sql
CREATE TABLE comptes_utilisateur_favoris (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utilisateur_id INTEGER NOT NULL,
    livre_id INTEGER NOT NULL,
    
    -- Contraintes de clés étrangères
    FOREIGN KEY (utilisateur_id) REFERENCES comptes_utilisateur(id) ON DELETE CASCADE,
    FOREIGN KEY (livre_id) REFERENCES bibliotheque_livre(id) ON DELETE CASCADE,
    
    -- Contrainte d'unicité pour éviter les doublons
    CONSTRAINT comptes_utilisateur_favoris_unique UNIQUE(utilisateur_id, livre_id)
);

-- Index pour optimiser les performances
CREATE INDEX idx_comptes_utilisateur_favoris_utilisateur_id ON comptes_utilisateur_favoris(utilisateur_id);
CREATE INDEX idx_comptes_utilisateur_favoris_livre_id ON comptes_utilisateur_favoris(livre_id);
```

## 📊 Tables de Données Système

### **11. `sqlite_sequence`**
```sql
-- Cette table est créée automatiquement par SQLite
-- Elle gère les séquences auto-incrémentées
-- Pas besoin de la créer manuellement
```

## 🚀 Script de Création Complet

```sql
-- =====================================================
-- SCRIPT COMPLET DE CRÉATION DE LA BASE BIBLIOTECH
-- =====================================================

-- Désactiver les contraintes de clés étrangères temporairement
PRAGMA foreign_keys = OFF;

-- Tables système Django
CREATE TABLE django_migrations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    app VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    applied DATETIME NOT NULL
);

CREATE TABLE django_content_type (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    app_label VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    UNIQUE(app_label, model)
);

CREATE TABLE django_session (
    session_key VARCHAR(40) PRIMARY KEY,
    session_data TEXT NOT NULL,
    expire_date DATETIME NOT NULL
);

-- Tables application bibliotheque
CREATE TABLE bibliotheque_auteur (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NULL
);

CREATE TABLE bibliotheque_categorie (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom VARCHAR(100) NOT NULL UNIQUE,
    image VARCHAR(255) NULL
);

CREATE TABLE bibliotheque_livre (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titre VARCHAR(200) NOT NULL,
    auteur_id INTEGER NULL,
    description TEXT NULL,
    image VARCHAR(255) NULL,
    numero_inventaire VARCHAR(50) NOT NULL UNIQUE,
    ancien_code VARCHAR(50) NULL,
    date_publication DATE NOT NULL,
    categorie_id INTEGER NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (auteur_id) REFERENCES bibliotheque_auteur(id) ON DELETE SET NULL,
    FOREIGN KEY (categorie_id) REFERENCES bibliotheque_categorie(id) ON DELETE SET NULL
);

-- Tables application comptes
CREATE TABLE comptes_utilisateur (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email VARCHAR(254) NOT NULL UNIQUE,
    mot_de_passe VARCHAR(128) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    nom VARCHAR(100) NOT NULL,
    type_utilisateur VARCHAR(20) NOT NULL,
    profession VARCHAR(100) NULL,
    institution VARCHAR(100) NULL,
    secteur_activite VARCHAR(100) NULL,
    adresse TEXT NULL,
    telephone VARCHAR(20) NULL,
    photo VARCHAR(255) NULL,
    date_inscription DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    derniere_connexion DATETIME NULL,
    est_actif BOOLEAN NOT NULL DEFAULT 1,
    est_admin BOOLEAN NOT NULL DEFAULT 0,
    est_bibliothecaire BOOLEAN NOT NULL DEFAULT 0,
    est_personnel BOOLEAN NOT NULL DEFAULT 0
);

CREATE TABLE comptes_rendezvous (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utilisateur_id INTEGER NOT NULL,
    statut VARCHAR(20) NOT NULL DEFAULT 'en_attente',
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    telephone VARCHAR(20) NOT NULL,
    email VARCHAR(254) NOT NULL,
    type_utilisateur VARCHAR(50) NOT NULL,
    titre_ouvrage VARCHAR(200) NULL,
    auteur_ouvrage VARCHAR(200) NULL,
    numero_inventaire VARCHAR(100) NULL,
    ancien_code VARCHAR(100) NULL,
    raison TEXT NOT NULL,
    date_souhaitee DATE NOT NULL,
    message TEXT NULL,
    date_creation DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    heure_entree TIME NULL,
    heure_sortie TIME NULL,
    livre_id INTEGER NOT NULL,
    FOREIGN KEY (utilisateur_id) REFERENCES comptes_utilisateur(id) ON DELETE CASCADE,
    FOREIGN KEY (livre_id) REFERENCES bibliotheque_livre(id) ON DELETE CASCADE
);

CREATE TABLE comptes_notification (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utilisateur_id INTEGER NOT NULL,
    message TEXT NOT NULL,
    url VARCHAR(255) NULL,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    lu BOOLEAN NOT NULL DEFAULT 0,
    FOREIGN KEY (utilisateur_id) REFERENCES comptes_utilisateur(id) ON DELETE CASCADE
);

-- Table de liaison pour les favoris
CREATE TABLE comptes_utilisateur_favoris (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    utilisateur_id INTEGER NOT NULL,
    livre_id INTEGER NOT NULL,
    FOREIGN KEY (utilisateur_id) REFERENCES comptes_utilisateur(id) ON DELETE CASCADE,
    FOREIGN KEY (livre_id) REFERENCES bibliotheque_livre(id) ON DELETE CASCADE,
    UNIQUE(utilisateur_id, livre_id)
);

-- Réactiver les contraintes de clés étrangères
PRAGMA foreign_keys = ON;

-- Création des index pour optimiser les performances
CREATE INDEX idx_bibliotheque_auteur_nom ON bibliotheque_auteur(nom);
CREATE INDEX idx_bibliotheque_categorie_nom ON bibliotheque_categorie(nom);
CREATE INDEX idx_bibliotheque_livre_titre ON bibliotheque_livre(titre);
CREATE INDEX idx_bibliotheque_livre_auteur_id ON bibliotheque_livre(auteur_id);
CREATE INDEX idx_bibliotheque_livre_categorie_id ON bibliotheque_livre(categorie_id);
CREATE INDEX idx_bibliotheque_livre_numero_inventaire ON bibliotheque_livre(numero_inventaire);
CREATE INDEX idx_comptes_utilisateur_email ON comptes_utilisateur(email);
CREATE INDEX idx_comptes_utilisateur_nom_prenom ON comptes_utilisateur(nom, prenom);
CREATE INDEX idx_comptes_rendezvous_utilisateur_id ON comptes_rendezvous(utilisateur_id);
CREATE INDEX idx_comptes_rendezvous_livre_id ON comptes_rendezvous(livre_id);
CREATE INDEX idx_comptes_rendezvous_statut ON comptes_rendezvous(statut);
CREATE INDEX idx_comptes_rendezvous_date_souhaitee ON comptes_rendezvous(date_souhaitee);
CREATE INDEX idx_comptes_notification_utilisateur_id ON comptes_notification(utilisateur_id);
CREATE INDEX idx_comptes_notification_created_at ON comptes_notification(created_at);
CREATE INDEX idx_comptes_utilisateur_favoris_utilisateur_id ON comptes_utilisateur_favoris(utilisateur_id);
CREATE INDEX idx_comptes_utilisateur_favoris_livre_id ON comptes_utilisateur_favoris(livre_id);

-- Message de confirmation
SELECT 'Base de données Bibliotech créée avec succès !' as message;
```

## 📝 Notes Importantes

### **Ordre de Création**
1. **Tables système Django** (sans dépendances)
2. **Tables bibliotheque** (sans dépendances entre elles)
3. **Tables comptes** (dépendent de bibliotheque)
4. **Tables de liaison** (dépendent des deux)

### **Contraintes de Validation**
- **Emails** : Format basique vérifié
- **Dates** : Dates futures pour les rendez-vous
- **Heures** : Cohérence entre entrée et sortie
- **Champs obligatoires** : Vérification de non-vide

### **Performance**
- **Index** créés sur tous les champs de recherche fréquents
- **Clés étrangères** avec suppression en cascade appropriée
- **Contraintes d'unicité** pour éviter les doublons

### **Sécurité**
- **Mots de passe** : Stockés avec hachage Django
- **Sessions** : Gérées par Django
- **Permissions** : Contrôlées par les champs booléens

**Ce script crée une base de données complète et optimisée pour Bibliotech !** 🎉
