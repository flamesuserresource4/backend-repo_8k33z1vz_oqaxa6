"""
Database Schemas

VoiceForge: Datenmodelle für Leads und leichtgewichtiges CMS

Jedes Pydantic-Modell entspricht einer Collection (Kleinbuchstaben des Klassennamens).
Beispiele:
- Lead -> "lead"
- Faq -> "faq"
- Section -> "section"
- TrustBadge -> "trustbadge"
"""

from pydantic import BaseModel, Field, EmailStr
from typing import Optional, Literal
from datetime import datetime

# Lead Schema
class Lead(BaseModel):
    firstName: str = Field(..., description="Vorname")
    lastName: str = Field(..., description="Nachname")
    company: str = Field(..., description="Firma")
    email: EmailStr = Field(..., description="E-Mail RFC 5322")
    phone: str = Field(..., pattern=r"^\+?[1-9]\d{7,14}$", description="Telefonnummer im E.164-Format")
    interest: Literal["Termin-Lead", "L1/L2", "Reminder", "After-Hours"] = Field(..., description="Interesse")
    startDate: Optional[datetime] = Field(None, description="Wunschzeitraum Start")
    endDate: Optional[datetime] = Field(None, description="Wunschzeitraum Ende")
    consent: bool = Field(..., description="Datenschutz akzeptiert")
    status: Literal["new", "contacted", "won", "lost"] = Field("new", description="Status")

# FAQ Schema
class Faq(BaseModel):
    slug: str = Field(..., description="Slug")
    question: str = Field(..., description="Frage")
    answerMd: str = Field(..., description="Antwort (Markdown)")
    order: int = Field(0, description="Reihenfolge")

# Section Schema
class Section(BaseModel):
    slug: str = Field(..., description="Slug")
    title: str = Field(..., description="Titel")
    contentMd: str = Field("", description="Inhalt (Markdown)")
    order: int = Field(0, description="Reihenfolge")
    visible: bool = Field(True, description="Sichtbar")

# TrustBadge Schema
class TrustBadge(BaseModel):
    slug: str = Field(..., description="Slug")
    title: str = Field(..., description="Titel")
    description: Optional[str] = Field(None, description="Beschreibung")
    order: int = Field(0, description="Reihenfolge")
