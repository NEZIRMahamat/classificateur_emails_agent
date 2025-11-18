from fastapi import FastAPI
from typing import List
import time
from groq import RateLimitError

from .app.config import settings
from .app.gmail_client import authenticate_gmail, get_all_emails
from .app.groq_client import TicketClassifier

# CHOISIS ICI TON MODE D'ÉCRITURE :
from .app.csv_writer import CSVWriter
# from .sheets_client import SheetWriter  # ← Active ceci si tu veux Google Sheets

from .app.models import ProcessResult, ProcessResponse

print("DEBUG → GROQ_API_KEY =", settings.groq_api_key)

app = FastAPI(
    title="Agent automatique de classification des tickets email",
    description="Lit les emails Gmail, analyse via Groq GPT-OSS, classe par catégorie et stocke les résultats.",
    version="1.0.0"
)

# Initialisation des services
gmail_service = authenticate_gmail()
classifier = TicketClassifier()

# Choisis ton writer :
csv_writer = CSVWriter()
# sheet_writer = SheetWriter()  # ← Active pour Google Sheets


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/process_all_emails", response_model=ProcessResponse)
def process_all_emails():
    """Traite tous les emails Gmail avec logs détaillés."""
    emails = get_all_emails(gmail_service)
    processed: List[ProcessResult] = []

    batch_size = 20
    total = len(emails)

    print("\n======================================")
    print(f" DÉBUT DU TRAITEMENT : {total} emails détectés")
    print("======================================\n")

    # Parcours email par email
    for index in range(0, total, batch_size):
        batch = emails[index:index + batch_size]
        batch_id = index // batch_size + 1

        print(f"🔄 Traitement batch {batch_id} ({len(batch)} emails)...\n")

        for mail in batch:
            subject = mail["subject"]
            body = mail["body"]

            print("\n----------------------------------------")
            print(f"📩 EMAIL EN COURS : {subject}")
            print("----------------------------------------")

            # Analyse via Groq (avec retry rate-limit)
            while True:
                try:
                    print("🧠 Analyse avec Groq...")
                    result = classifier.classify(subject, body)
                    break
                except RateLimitError:
                    wait = 25
                    print(f"⏳ Rate-limit Groq → pause {wait}s...")
                    time.sleep(wait)

            categorie = result["categorie"]
            urgence = result["urgence"]
            resume = result["resume"]

            print(f"📌 Catégorie détectée : {categorie}")
            print(f"⚠️  Urgence : {urgence}")
            print(f"📝 Résumé : {resume[:150]}...")

            # Sauvegarde CSV ou Google Sheets
            print(f"📤 Enregistrement dans : {categorie}")

            # 👉 Mode CSV
            csv_writer.append_ticket(categorie, subject, urgence, resume)

            # 👉 Mode Google Sheets
            # sheet_writer.append_ticket(categorie, subject, urgence, resume)

            print("✅ Ligne enregistrée avec succès.")

            processed.append(
                ProcessResult(
                    subject=subject,
                    body_preview=body[:200],
                    categorie=categorie,
                    urgence=urgence,
                    resume=resume,
                )
            )

        print(f"\n✔️ Batch {batch_id} terminé ({len(processed)}/{total})\n")

    print("\n🎉 TRAITEMENT TERMINÉ — TOUS LES EMAILS ONT ÉTÉ ANALYSÉS.\n")

    return ProcessResponse(
        total_emails=total,
        processed=processed
    )
