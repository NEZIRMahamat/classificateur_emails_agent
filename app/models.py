# app/models.py
from typing import List
from pydantic import BaseModel


class ProcessResult(BaseModel):
    subject: str
    body_preview: str
    categorie: str
    urgence: str
    resume: str


class ProcessResponse(BaseModel):
    total_emails: int
    processed: List[ProcessResult]
