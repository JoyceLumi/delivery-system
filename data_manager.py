import json
import os

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")


class DataManager:

    def __init__(self):
        os.makedirs(DATA_DIR, exist_ok=True)

    def _lire_json(self, fichier):
        chemin = os.path.join(DATA_DIR, fichier)
        if not os.path.exists(chemin):
            return []
        with open(chemin, "r", encoding="utf-8") as f:
            return json.load(f)

    def _ecrire_json(self, fichier, data):
        chemin = os.path.join(DATA_DIR, fichier)
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    def sauvegarder_clients(self, clients):
        self._ecrire_json("clients.json", clients)

    def sauvegarder_livreurs(self, livreurs):
        self._ecrire_json("livreurs.json", livreurs)

    def sauvegarder_commandes(self, commandes):
        self._ecrire_json("commandes.json", commandes)

    def charger_clients(self):
        return self._lire_json("clients.json")

    def charger_livreurs(self):
        return self._lire_json("livreurs.json")

    def charger_commandes(self):
        return self._lire_json("commandes.json")

    def charger_tout(self):
        return {
            "clients": self.charger_clients(),
            "livreurs": self.charger_livreurs(),
            "commandes": self.charger_commandes()
        }
