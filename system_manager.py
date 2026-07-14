from datetime import datetime
from models.client import Client
from models.livreur import Livreur, StatutLivreur
from models.commande import Commande, StatutCommande
from models.paiement import PaiementCash, PaiementMobile, PaiementCarte
from models.livraison import Livraison
from strategies.cout_livraison import CoutStandard, CoutExpress
from data_manager import DataManager
from exceptions import LivraisonErreur, CommandeErreur

MODE_PAIEMENT_MAP = {
    "PaiementCash": "Espèces",
    "PaiementMobile": "Mobile Money",
    "PaiementCarte": "Carte bancaire",
}
MODE_PAIEMENT_REVERSE = {v: k for k, v in MODE_PAIEMENT_MAP.items()}
CLASSE_PAIEMENT = {
    "Espèces": PaiementCash,
    "Mobile Money": PaiementMobile,
    "Carte bancaire": PaiementCarte,
}


class SystemManager:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
        self._initialized = True
        self.data_manager = DataManager()
        try:
            data = self.data_manager.charger_tout()
            self.clients = [Client.from_dict(c) for c in data["clients"]]
            self.livreurs = [Livreur.from_dict(l) for l in data["livreurs"]]
            self.commandes = [
                Commande.from_dict(c, self.clients, self.livreurs)
                for c in data["commandes"]
            ]
        except Exception as e:
            raise LivraisonErreur(f"Erreur lors du chargement des données : {e}")

        self.strategies_cout = {
            "Standard": CoutStandard(),
            "Express": CoutExpress(),
        }

    # --- Clients ---

    def ajouter_client(self, nom, prenom, telephone, email="", adresse=""):
        try:
            client_id = max((c.id for c in self.clients), default=0) + 1
            client = Client(client_id, nom, prenom, telephone, email, adresse)
            self.clients.append(client)
            self._sauvegarder()
            return client
        except Exception as e:
            raise CommandeErreur(f"Erreur ajout client : {e}")

    def modifier_client(self, client_id, **kwargs):
        for c in self.clients:
            if c.id == client_id:
                for k, v in kwargs.items():
                    setattr(c, k, v)
                self._sauvegarder()
                return True
        return False

    def supprimer_client(self, client_id):
        self.clients = [c for c in self.clients if c.id != client_id]
        self._sauvegarder()

    def get_client(self, client_id):
        for c in self.clients:
            if c.id == client_id:
                return c
        return None

    # --- Livreurs ---

    def ajouter_livreur(self, nom, prenom, telephone):
        try:
            livreur_id = max((l.id for l in self.livreurs), default=0) + 1
            livreur = Livreur(livreur_id, nom, prenom, telephone)
            self.livreurs.append(livreur)
            self._sauvegarder()
            return livreur
        except Exception as e:
            raise LivraisonErreur(f"Erreur ajout livreur : {e}")

    def modifier_statut_livreur(self, livreur_id, statut):
        for l in self.livreurs:
            if l.id == livreur_id:
                l.statut = statut
                self._sauvegarder()
                return True
        return False

    def mettre_a_jour_position(self, livreur_id, latitude, longitude):
        for l in self.livreurs:
            if l.id == livreur_id:
                l.latitude = latitude
                l.longitude = longitude
                self._sauvegarder()
                return True
        return False

    def livreurs_disponibles(self):
        return [l for l in self.livreurs if l.statut == StatutLivreur.DISPONIBLE]

    # --- Commandes ---

    def creer_commande(self, client, adresse_livraison, heure_prevue,
                       montant=0.0, livreur=None):
        try:
            commande_id = max((c.id for c in self.commandes), default=0) + 1
            commande = Commande(
                commande_id, client, adresse_livraison, heure_prevue,
                montant, livreur,
            )
            self.commandes.append(commande)
            if livreur:
                livreur.statut = StatutLivreur.OCCUPE
            self._sauvegarder()
            return commande
        except Exception as e:
            raise CommandeErreur(f"Erreur création commande : {e}")

    def assigner_livreur(self, commande, livreur):
        commande.livreur = livreur
        commande.statut = StatutCommande.EN_COURS
        livreur.statut = StatutLivreur.OCCUPE
        self._sauvegarder()

    def mettre_a_jour_statut_commande(self, commande, statut):
        commande.statut = statut
        if statut == StatutCommande.LIVRE:
            commande.heure_reelle_livraison = datetime.now().strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            if commande.livreur:
                commande.livreur.statut = StatutLivreur.DISPONIBLE
        self._sauvegarder()

    def mettre_a_jour_position_livraison(self, commande, latitude, longitude):
        commande.livreur_latitude = latitude
        commande.livreur_longitude = longitude
        if commande.livreur:
            commande.livreur.latitude = latitude
            commande.livreur.longitude = longitude
        self._sauvegarder()

    def payer_commande(self, commande, mode_display):
        cls = CLASSE_PAIEMENT.get(mode_display)
        if not cls:
            return False
        try:
            paiement = cls(commande.montant)
            if paiement.payer():
                commande.paiement = paiement
                self._sauvegarder()
                return True
            return False
        except Exception as e:
            raise CommandeErreur(f"Erreur paiement : {e}")

    def calculer_cout_livraison(self, distance_km, type_cout="Standard"):
        strategy = self.strategies_cout.get(
            type_cout, self.strategies_cout["Standard"]
        )
        return strategy.calculer(distance_km)

    def est_en_retard(self, commande):
        if not commande.heure_reelle_livraison:
            return False
        try:
            prevue = datetime.strptime(
                commande.heure_prevue, "%Y-%m-%d %H:%M"
            )
        except ValueError:
            prevue = datetime.strptime(
                commande.heure_prevue, "%Y-%m-%d %H:%M:%S"
            )
        reelle = datetime.strptime(
            commande.heure_reelle_livraison, "%Y-%m-%d %H:%M:%S"
        )
        return reelle > prevue

    def creer_livraison(self, commande):
        return Livraison(commande)

    def _sauvegarder(self):
        self.data_manager.sauvegarder_clients(
            [c.to_dict() for c in self.clients]
        )
        self.data_manager.sauvegarder_livreurs(
            [l.to_dict() for l in self.livreurs]
        )
        self.data_manager.sauvegarder_commandes(
            [c.to_dict() for c in self.commandes]
        )
