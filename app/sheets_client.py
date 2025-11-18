# app/sheets_client.py
import os
from typing import Literal
import gspread
from google.oauth2.service_account import Credentials

from .groq_client import CATEGORIES

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]


class SheetWriter:
    def __init__(self):
        sheet_id = os.getenv("GOOGLE_SHEET_ID")
        if not sheet_id:
            raise ValueError("GOOGLE_SHEET_ID manquant dans l'environnement")

        creds = Credentials.from_service_account_file(
            "credentials/service_account.json",
            scopes=SCOPES,
        )

        self.gc = gspread.authorize(creds)
        self.sh = self.gc.open_by_key(sheet_id)

    def append_ticket(self, categorie: str, sujet: str, urgence: str, resume: str):
        """
        Ajoute une ligne dans la feuille correspondant à la catégorie.
        On suppose que le nom de l'onglet == nom de la catégorie.
        """
        if categorie not in CATEGORIES:
            categorie = CATEGORIES[0]

        try:
            worksheet = self.sh.worksheet(categorie)
        except gspread.WorksheetNotFound:
            # Si l'onglet n'existe pas, on peut le créer
            worksheet = self.sh.add_worksheet(title=categorie, rows=1000, cols=3)
            worksheet.append_row(["Sujet", "Urgence", "Synthèse"])

        # Ajouter la ligne
        worksheet.append_row([sujet, urgence, resume], value_input_option="USER_ENTERED")


# Test rapide possible
if __name__ == "__main__":
    writer = SheetWriter()
    writer.append_ticket(
        "Problème technique informatique",
        "Test sujet",
        "Modérée",
        "Ceci est un test de synthèse."
    )
    print("Ligne ajoutée.")
