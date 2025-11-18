# app/csv_writer.py
import os
import csv
from .groq_client import CATEGORIES

DATA_FOLDER = "data"


def category_to_filename(categorie: str) -> str:
    """
    Transforme le nom de catégorie en nom de fichier 'safe'.
    Exemple :
    'Problème d’accès / authentification'
      -> 'Probleme_d_acces___authentification.csv'
    """
    safe = []
    for c in categorie:
        if c.isalnum():
            safe.append(c)
        elif c in (" ", "_", "-"):
            safe.append("_")
        else:
            safe.append("_")
    return "".join(safe) + ".csv"


class CSVWriter:
    def __init__(self):
        # Crée le dossier data/ au besoin
        os.makedirs(DATA_FOLDER, exist_ok=True)

        # S'assure que chaque catégorie a un CSV avec en-tête
        for categorie in CATEGORIES:
            path = os.path.join(DATA_FOLDER, category_to_filename(categorie))
            if not os.path.exists(path):
                with open(path, "w", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    writer.writerow(["Sujet", "Urgence", "Synthèse"])

    def append_ticket(self, categorie: str, sujet: str, urgence: str, resume: str):
        """
        Ajoute une ligne dans le CSV correspondant à la catégorie.
        Si la catégorie n'est pas reconnue, on la met dans la première.
        """
        if categorie not in CATEGORIES:
            categorie = CATEGORIES[0]

        path = os.path.join(DATA_FOLDER, category_to_filename(categorie))

        file_exists = os.path.exists(path)
        with open(path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["Sujet", "Urgence", "Synthèse"])
            writer.writerow([sujet, urgence, resume])
