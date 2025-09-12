-- Script SQL pour initialiser les tables Supabase
-- Exécuter ces commandes dans l'éditeur SQL de Supabase

-- 1. Table des catégories
CREATE TABLE IF NOT EXISTS categories (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    image TEXT, -- URL de l'image
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. Table des auteurs
CREATE TABLE IF NOT EXISTS auteurs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Table des livres
CREATE TABLE IF NOT EXISTS livres (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    titre VARCHAR(200) NOT NULL,
    auteur_id UUID REFERENCES auteurs(id) ON DELETE SET NULL,
    description TEXT,
    image TEXT, -- URL de l'image
    numero_inventaire VARCHAR(50) UNIQUE NOT NULL,
    ancien_code VARCHAR(50),
    date_publication DATE NOT NULL,
    categorie_id UUID REFERENCES categories(id) ON DELETE SET NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Table des rendez-vous (si elle n'existe pas déjà)
CREATE TABLE IF NOT EXISTS rendezvous (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    utilisateur_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    statut VARCHAR(20) DEFAULT 'en_attente' CHECK (statut IN ('en_attente', 'confirme', 'annule', 'termine')),
    
    -- Informations personnelles
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    telephone VARCHAR(20) NOT NULL,
    email VARCHAR(255) NOT NULL,
    type_utilisateur VARCHAR(50) NOT NULL,
    
    -- Lien vers le livre
    livre_id UUID REFERENCES livres(id) ON DELETE CASCADE,
    
    -- Champs redondants pour archivage
    titre_ouvrage VARCHAR(200),
    auteur_ouvrage VARCHAR(200),
    numero_inventaire VARCHAR(100),
    ancien_code VARCHAR(100),
    
    -- Détails du rendez-vous
    raison TEXT NOT NULL,
    date_souhaitee DATE NOT NULL,
    message TEXT,
    date_creation TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Heures d'entrée/sortie
    heure_entree TIME,
    heure_sortie TIME
);

-- 5. Table des notifications (si elle n'existe pas déjà)
CREATE TABLE IF NOT EXISTS notifications (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    utilisateur_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    message TEXT NOT NULL,
    url VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    lu BOOLEAN DEFAULT FALSE
);

-- 6. Table des profils (si elle n'existe pas déjà)
CREATE TABLE IF NOT EXISTS profiles (
    id UUID REFERENCES auth.users(id) ON DELETE CASCADE PRIMARY KEY,
    email VARCHAR(255) NOT NULL,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    adresse TEXT,
    telephone VARCHAR(20),
    secteur_activite VARCHAR(100),
    institution VARCHAR(100),
    profession VARCHAR(100),
    profil VARCHAR(50) DEFAULT 'etudiant',
    is_admin BOOLEAN DEFAULT FALSE,
    is_administration BOOLEAN DEFAULT FALSE,
    is_librarian BOOLEAN DEFAULT FALSE,
    is_user BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 7. Table des favoris (relation many-to-many)
CREATE TABLE IF NOT EXISTS favoris (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    utilisateur_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    livre_id UUID REFERENCES livres(id) ON DELETE CASCADE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(utilisateur_id, livre_id)
);

-- Index pour optimiser les performances
CREATE INDEX IF NOT EXISTS idx_livres_categorie ON livres(categorie_id);
CREATE INDEX IF NOT EXISTS idx_livres_auteur ON livres(auteur_id);
CREATE INDEX IF NOT EXISTS idx_rendezvous_utilisateur ON rendezvous(utilisateur_id);
CREATE INDEX IF NOT EXISTS idx_rendezvous_livre ON rendezvous(livre_id);
CREATE INDEX IF NOT EXISTS idx_notifications_utilisateur ON notifications(utilisateur_id);
CREATE INDEX IF NOT EXISTS idx_favoris_utilisateur ON favoris(utilisateur_id);
CREATE INDEX IF NOT EXISTS idx_favoris_livre ON favoris(livre_id);

-- RLS (Row Level Security) - Politiques de sécurité
ALTER TABLE categories ENABLE ROW LEVEL SECURITY;
ALTER TABLE auteurs ENABLE ROW LEVEL SECURITY;
ALTER TABLE livres ENABLE ROW LEVEL SECURITY;
ALTER TABLE rendezvous ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications ENABLE ROW LEVEL SECURITY;
ALTER TABLE profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE favoris ENABLE ROW LEVEL SECURITY;

-- Politiques pour permettre la lecture à tous les utilisateurs authentifiés
CREATE POLICY "Lecture publique des catégories" ON categories FOR SELECT USING (true);
CREATE POLICY "Lecture publique des auteurs" ON auteurs FOR SELECT USING (true);
CREATE POLICY "Lecture publique des livres" ON livres FOR SELECT USING (true);

-- Politiques pour les profils
CREATE POLICY "Utilisateurs peuvent voir leur propre profil" ON profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Utilisateurs peuvent modifier leur propre profil" ON profiles FOR UPDATE USING (auth.uid() = id);

-- Politiques pour les rendez-vous
CREATE POLICY "Utilisateurs peuvent voir leurs propres RDV" ON rendezvous FOR SELECT USING (auth.uid() = utilisateur_id);
CREATE POLICY "Utilisateurs peuvent créer des RDV" ON rendezvous FOR INSERT WITH CHECK (auth.uid() = utilisateur_id);
CREATE POLICY "Utilisateurs peuvent modifier leurs propres RDV" ON rendezvous FOR UPDATE USING (auth.uid() = utilisateur_id);

-- Politiques pour les notifications
CREATE POLICY "Utilisateurs peuvent voir leurs propres notifications" ON notifications FOR SELECT USING (auth.uid() = utilisateur_id);
CREATE POLICY "Utilisateurs peuvent marquer leurs notifications comme lues" ON notifications FOR UPDATE USING (auth.uid() = utilisateur_id);

-- Politiques pour les favoris
CREATE POLICY "Utilisateurs peuvent gérer leurs propres favoris" ON favoris FOR ALL USING (auth.uid() = utilisateur_id);

-- Politiques pour les bibliothécaires (lecture/écriture complète)
CREATE POLICY "Bibliothécaires peuvent tout faire sur les catégories" ON categories FOR ALL USING (
    EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND is_librarian = true)
);
CREATE POLICY "Bibliothécaires peuvent tout faire sur les auteurs" ON auteurs FOR ALL USING (
    EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND is_librarian = true)
);
CREATE POLICY "Bibliothécaires peuvent tout faire sur les livres" ON livres FOR ALL USING (
    EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND is_librarian = true)
);
CREATE POLICY "Bibliothécaires peuvent voir tous les RDV" ON rendezvous FOR SELECT USING (
    EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND is_librarian = true)
);
CREATE POLICY "Bibliothécaires peuvent modifier tous les RDV" ON rendezvous FOR UPDATE USING (
    EXISTS (SELECT 1 FROM profiles WHERE id = auth.uid() AND is_librarian = true)
);

-- Fonction pour mettre à jour updated_at automatiquement
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers pour updated_at
CREATE TRIGGER update_categories_updated_at BEFORE UPDATE ON categories FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_auteurs_updated_at BEFORE UPDATE ON auteurs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_livres_updated_at BEFORE UPDATE ON livres FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
