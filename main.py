import os
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field

from database import create_document, db

app = FastAPI(title="VoiceForge API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class LeadIn(BaseModel):
    firstName: str = Field(..., min_length=1)
    lastName: str = Field(..., min_length=1)
    company: str = Field(..., min_length=1)
    email: EmailStr
    phone: str = Field(..., pattern=r"^\+?[1-9]\d{7,14}$")
    interest: str = Field(..., pattern=r"^(Termin-Lead|L1/L2|Reminder|After-Hours)$")
    startDate: Optional[datetime] = None
    endDate: Optional[datetime] = None
    consent: bool


@app.get("/")
def root():
    return {"message": "VoiceForge Backend bereit"}


@app.post("/api/lead")
def create_lead_endpoint(lead: LeadIn):
    if not lead.consent:
        raise HTTPException(status_code=400, detail="Bitte stimmen Sie der Datenverarbeitung zu.")

    doc = lead.model_dump()
    doc["status"] = "new"
    doc["createdAt"] = datetime.utcnow()
    _id = create_document("lead", doc)

    return {"ok": True, "id": _id}


# ----------------- Lightweight CMS Endpoints -----------------
@app.get("/api/faqs")
def get_faqs():
    try:
        items = list(db["faq"].find({}, {"_id": 0}).sort("order", 1)) if db else []
        return {"items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/sections")
def get_sections():
    try:
        items = list(db["section"].find({}, {"_id": 0}).sort("order", 1)) if db else []
        return {"items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/trust-badges")
def get_trust_badges():
    try:
        items = list(db["trustbadge"].find({}, {"_id": 0}).sort("order", 1)) if db else []
        return {"items": items}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ----------------- Seeder on startup -----------------
@app.on_event("startup")
async def seed_cms():
    if db is None:
        return
    # Seed Sections
    if db["section"].count_documents({}) == 0:
        db["section"].insert_many([
            {"slug": "hero", "title": "KI Voice Agents für Ihr Unternehmen", "contentMd": "", "order": 1, "visible": True},
            {"slug": "challenges", "title": "Ihre Herausforderungen", "contentMd": "", "order": 2, "visible": True},
            {"slug": "solutions", "title": "Unsere Lösungen", "contentMd": "", "order": 3, "visible": True},
            {"slug": "demo", "title": "Live-Demo buchen", "contentMd": "", "order": 4, "visible": True},
            {"slug": "trust", "title": "Vertrauen & Sicherheit", "contentMd": "", "order": 5, "visible": True},
            {"slug": "faq", "title": "Häufige Fragen", "contentMd": "", "order": 6, "visible": True},
        ])
    # Seed Badges
    if db["trustbadge"].count_documents({}) == 0:
        db["trustbadge"].insert_many([
            {"slug": "gdpr", "title": "DSGVO-konform", "description": "Datenverarbeitung in der EU", "order": 1},
            {"slug": "iso", "title": "ISO-zertifiziert", "description": "Sichere Prozesse & Audits", "order": 2},
            {"slug": "made-de", "title": "Made in Germany", "description": "Entwickelt & betrieben in DE", "order": 3},
        ])
    # Seed FAQs (8-10)
    if db["faq"].count_documents({}) == 0:
        faqs = [
            {"slug": "ai-transparenz", "question": "Spreche ich mit einer KI?", "answerMd": "Ja. Sie sprechen mit einem KI-Assistenten. Eine Weiterleitung zu Mitarbeitenden ist jederzeit möglich.", "order": 1},
            {"slug": "verfugbarkeit", "question": "Ist der Service 24/7 erreichbar?", "answerMd": "Ja, Ihre Anrufer werden rund um die Uhr betreut – auch an Wochenenden und Feiertagen.", "order": 2},
            {"slug": "integration", "question": "Wie integriert sich VoiceForge?", "answerMd": "Wir verbinden uns mit Kalendern, Ticket-Tools und CRM-Systemen per API.", "order": 3},
            {"slug": "datenschutz", "question": "Wie wird Datenschutz gewährleistet?", "answerMd": "DSGVO-konform mit EU-Hosting, AVV auf Anfrage.", "order": 4},
            {"slug": "preise", "question": "Wie sind die Preise?", "answerMd": "Transparente Pakete je nach Volumen. Sie erhalten ein Angebot nach der Demo.", "order": 5},
            {"slug": "setup", "question": "Wie lange dauert das Setup?", "answerMd": "In der Regel 1–2 Wochen bis zum Go-Live.", "order": 6},
            {"slug": "notfall", "question": "Werden Notfälle erkannt?", "answerMd": "Ja, Notfall-Stichworte werden priorisiert und entsprechend eskaliert.", "order": 7},
            {"slug": "kanale", "question": "Unterstützte Kanäle?", "answerMd": "Telefon, Chat, E-Mail und WhatsApp – Omnichannel.", "order": 8},
            {"slug": "support", "question": "Was ist mit L1/L2-Support?", "answerMd": "L1-Triage mit Wissensdatenbank und strukturierter Eskalation an L2.", "order": 9},
            {"slug": "pilot", "question": "Gibt es einen Pilot?", "answerMd": "Ja. Nach der Demo erhalten Sie einen ersten Prototypen.", "order": 10},
        ]
        db["faq"].insert_many(faqs)


@app.get("/test")
def test_database():
    response = {
        "backend": "✅ Running",
        "database": "❌ Not Available",
        "database_url": None,
        "database_name": None,
        "connection_status": "Not Connected",
        "collections": []
    }

    try:
        if db is not None:
            response["database"] = "✅ Connected & Working"
            response["database_url"] = "✅ Set" if os.getenv("DATABASE_URL") else "❌ Not Set"
            response["database_name"] = db.name
            response["connection_status"] = "Connected"
            try:
                collections = db.list_collection_names()
                response["collections"] = collections[:10]
            except Exception as e:
                response["database"] = f"⚠️ Connected but Error: {str(e)[:80]}"
        else:
            response["database"] = "⚠️ Available but not initialized"
    except Exception as e:
        response["database"] = f"❌ Error: {str(e)[:80]}"

    return response


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
