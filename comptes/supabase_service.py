from bibliotech.supabase_client import supabase, supabase_admin
from typing import List, Dict, Optional
import uuid

class SupabaseService:
    def __init__(self):
        self.client = supabase
        self.admin_client = supabase_admin
    
    # Méthodes pour l'authentification
    def sign_up(self, email: str, password: str, user_data: Dict) -> Dict:
        """Inscription d'un utilisateur"""
        try:
            # Vérifier si l'utilisateur existe déjà
            existing_user = self.client.table('profiles').select('id').eq('email', email).execute()
            if existing_user.data:
                return {"success": False, "error": "Un utilisateur avec cet email existe déjà"}
            
            # Créer l'utilisateur dans auth.users avec les données dans raw_user_meta_data
            auth_response = self.client.auth.sign_up({
                "email": email,
                "password": password,
                "options": {
                    "data": user_data
                }
            })
            
            if auth_response.user:
                # Le profil est créé automatiquement par la fonction handle_new_user()
                # Récupérer le profil créé
                profile_response = self.client.table('profiles').select('*').eq('id', auth_response.user.id).execute()
                
                if profile_response.data:
                    return {
                        "success": True,
                        "user": auth_response.user,
                        "profile": profile_response.data[0]
                    }
                else:
                    return {"success": False, "error": "Profil non trouvé après création"}
            else:
                return {"success": False, "error": "Erreur lors de la création de l'utilisateur"}
                
        except Exception as e:
            import traceback
            error_msg = str(e)
            traceback_str = traceback.format_exc()
            print(f"Erreur détaillée: {error_msg}")
            print(f"Traceback: {traceback_str}")
            return {"success": False, "error": f"Erreur d'inscription: {error_msg}"}
    
    def sign_in(self, email: str, password: str) -> Dict:
        """Connexion d'un utilisateur"""
        try:
            response = self.client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            if response.user:
                # Récupérer le profil
                profile = self.get_profile_by_id(response.user.id)
                return {
                    "success": True,
                    "user": response.user,
                    "profile": profile
                }
            else:
                return {"success": False, "error": "Identifiants incorrects"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def sign_out(self) -> bool:
        """Déconnexion"""
        try:
            self.client.auth.sign_out()
            return True
        except Exception as e:
            print(f"Erreur lors de la déconnexion: {e}")
            return False
    
    # Méthodes pour les profils
    def get_profile_by_id(self, user_id: str) -> Optional[Dict]:
        """Récupère un profil par ID utilisateur"""
        try:
            result = self.client.table('profiles').select('*').eq('id', user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erreur lors de la récupération du profil: {e}")
            return None
    
    def get_profile_by_email(self, email: str) -> Optional[Dict]:
        """Récupère un profil par email"""
        try:
            result = self.client.table('profiles').select('*').eq('email', email).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erreur lors de la récupération du profil: {e}")
            return None
    
    def update_profile(self, user_id: str, profile_data: Dict) -> Optional[Dict]:
        """Met à jour un profil"""
        try:
            result = self.client.table('profiles').update(profile_data).eq('id', user_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erreur lors de la mise à jour du profil: {e}")
            return None
    
    # Méthodes pour les rendez-vous
    def get_rendezvous_by_user(self, user_id: str) -> List[Dict]:
        """Récupère les rendez-vous d'un utilisateur"""
        try:
            result = self.client.table('rendezvous').select('*').eq('utilisateur_id', user_id).execute()
            return result.data
        except Exception as e:
            print(f"Erreur lors de la récupération des rendez-vous: {e}")
            return []
    
    def create_rendezvous(self, rdv_data: Dict) -> Optional[Dict]:
        """Crée un nouveau rendez-vous"""
        try:
            result = self.client.table('rendezvous').insert(rdv_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erreur lors de la création du rendez-vous: {e}")
            return None
    
    # Méthodes pour les notifications
    def get_notifications_by_user(self, user_id: str) -> List[Dict]:
        """Récupère les notifications d'un utilisateur"""
        try:
            result = self.client.table('notifications').select('*').eq('utilisateur_id', user_id).execute()
            return result.data
        except Exception as e:
            print(f"Erreur lors de la récupération des notifications: {e}")
            return []
    
    def mark_notification_as_read(self, notification_id: str) -> bool:
        """Marque une notification comme lue"""
        try:
            result = self.client.table('notifications').update({'lu': True}).eq('id', notification_id).execute()
            return True
        except Exception as e:
            print(f"Erreur lors de la mise à jour de la notification: {e}")
            return False
    
    # Méthodes pour les livres
    def get_all_livres(self) -> List[Dict]:
        """Récupère tous les livres"""
        try:
            result = self.client.table('livres').select('*').execute()
            return result.data
        except Exception as e:
            print(f"Erreur lors de la récupération des livres: {e}")
            return []
    
    def search_livres(self, query: str) -> List[Dict]:
        """Recherche des livres"""
        try:
            result = self.client.table('livres').select('*').ilike('titre', f'%{query}%').execute()
            return result.data
        except Exception as e:
            print(f"Erreur lors de la recherche de livres: {e}")
            return []
    
    # Méthodes pour les catégories
    def get_all_categories(self) -> List[Dict]:
        """Récupère toutes les catégories"""
        try:
            result = self.client.table('categories').select('*').execute()
            return result.data
        except Exception as e:
            print(f"Erreur lors de la récupération des catégories: {e}")
            return []
    
    def create_categorie(self, categorie_data: Dict) -> Optional[Dict]:
        """Crée une nouvelle catégorie"""
        try:
            result = self.client.table('categories').insert(categorie_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erreur lors de la création de la catégorie: {e}")
            return None
    
    def get_categorie_by_id(self, categorie_id: str) -> Optional[Dict]:
        """Récupère une catégorie par ID"""
        try:
            result = self.client.table('categories').select('*').eq('id', categorie_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erreur lors de la récupération de la catégorie: {e}")
            return None
    
    def get_livres_by_categorie(self, categorie_id: str) -> List[Dict]:
        """Récupère les livres d'une catégorie"""
        try:
            result = self.client.table('livres').select('*').eq('categorie_id', categorie_id).execute()
            return result.data
        except Exception as e:
            print(f"Erreur lors de la récupération des livres par catégorie: {e}")
            return []
    
    def get_livre_by_id(self, livre_id: str) -> Optional[Dict]:
        """Récupère un livre par ID"""
        try:
            result = self.client.table('livres').select('*').eq('id', livre_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erreur lors de la récupération du livre: {e}")
            return None
    
    def create_livre(self, livre_data: Dict) -> Optional[Dict]:
        """Crée un nouveau livre"""
        try:
            result = self.client.table('livres').insert(livre_data).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erreur lors de la création du livre: {e}")
            return None
    
    def update_livre(self, livre_id: str, livre_data: Dict) -> Optional[Dict]:
        """Met à jour un livre"""
        try:
            result = self.client.table('livres').update(livre_data).eq('id', livre_id).execute()
            return result.data[0] if result.data else None
        except Exception as e:
            print(f"Erreur lors de la mise à jour du livre: {e}")
            return None
    
    def delete_livre(self, livre_id: str) -> bool:
        """Supprime un livre"""
        try:
            result = self.client.table('livres').delete().eq('id', livre_id).execute()
            return True
        except Exception as e:
            print(f"Erreur lors de la suppression du livre: {e}")
            return False