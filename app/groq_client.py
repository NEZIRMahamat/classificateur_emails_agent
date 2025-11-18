# app/groq_client.py
import os
import json
from groq import Groq

# Liste des catégories imposées par l’énoncé
CATEGORIES = [
    "Problème technique informatique",
    "Demande administrative",
    "Problème d’accès / authentification",
    "Demande de support utilisateur",
    "Bug ou dysfonctionnement d’un service",
]

# Niveaux d’urgence imposés
URGENCES = [
    "Anodine",
    "Faible",
    "Modérée",
    "Élevée",
    "Critique",
]


class TicketClassifier:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY manquant dans l'environnement")

        # Client Groq (API compatible OpenAI)
        self.client = Groq(api_key=api_key)

        # Modèle GPT-like via Groq
        self.model_name = "openai/gpt-oss-20b"  # ou "openai/gpt-oss-120b"

    def classify(self, subject: str, body: str) -> dict:
        """
        Analyse un ticket et renvoie :
        {
            "categorie": str,
            "urgence": str,
            "resume": str
        }
        """
        system_prompt = (
            "Tu es un assistant qui analyse des tickets informatiques reçus par email.\n"
            "À partir du sujet et du contenu du message, tu dois :\n"
            f"- déterminer la catégorie EXACTEMENT parmi : {', '.join(CATEGORIES)}\n"
            f"- déterminer le niveau d'urgence EXACTEMENT parmi : {', '.join(URGENCES)}\n"
            "- produire un résumé court en français (1 à 3 phrases).\n\n"
            "Réponds STRICTEMENT en JSON, sans texte autour, au format :\n"
            '{"categorie": "...", "urgence": "...", "resume": "..."}'
        )

        user_content = f"Sujet : {subject}\n\nContenu :\n{body}"

        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_content},
            ],
            temperature=0.2,
        )

        content = completion.choices[0].message.content.strip()

        try:
            data = json.loads(content)
        except json.JSONDecodeError:
            # fallback basique si le modèle ne renvoie pas du JSON propre
            data = {
                "categorie": CATEGORIES[0],
                "urgence": "Modérée",
                "resume": content[:200],
            }

        # Sécurisation des valeurs
        if data.get("categorie") not in CATEGORIES:
            data["categorie"] = CATEGORIES[0]
        if data.get("urgence") not in URGENCES:
            data["urgence"] = "Modérée"

        if "resume" not in data or not isinstance(data["resume"], str):
            data["resume"] = ""

        return data


if __name__ == "__main__":
    # petit test manuel
    clf = TicketClassifier()
    res = clf.classify(
        "Problème de connexion",
        "Je ne peux plus me connecter à mon compte depuis ce matin, erreur 403."
    )
    print(res)
