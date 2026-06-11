"""Lead Ingestion API — tum kaynaklardan tek noktadan lead alir.

Akis: auth -> normalize -> skor/segment/takip -> AI satis notu -> PG upsert -> Gmail bildirim.
"""
from __future__ import annotations

import logging
import os
import secrets
from contextlib import asynccontextmanager
from typing import Literal

import anyio
from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field

from . import db, insight, notify, pipeline

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("lead-ingestion")


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await db.close_pool()


app = FastAPI(title="Lead Ingestion API", version="1.0.0", lifespan=lifespan)

Source = Literal["Site", "Meta Ads", "WhatsApp", "IG DM", "LinkedIn", "Clay", "Manuel"]


class LeadIn(BaseModel):
    source: Source
    external_id: str = Field(min_length=1, max_length=255)
    leadgen_id: str | None = None
    ad_soyad: str = Field(min_length=1, max_length=255)
    email: str | None = None
    telefon: str | None = None
    sirket_adi: str | None = None
    sektor: str | None = None
    konum: str | None = None
    butce: str | int | None = None
    mesaj: str | None = None
    raw: dict = Field(default_factory=dict)


class LeadOut(BaseModel):
    id: int
    deduped: bool
    skor: int
    segment: str
    asama: str
    takip_tarihi: str


def _check_auth(secret: str | None) -> None:
    expected = os.getenv("INGEST_SHARED_SECRET")
    if not expected or not secret or not secrets.compare_digest(secret, expected):
        raise HTTPException(status_code=401, detail="unauthorized")


@app.get("/healthz")
async def healthz():
    return {"status": "ok"}


@app.post("/leads/ingest", response_model=LeadOut)
async def ingest_lead(payload: LeadIn, x_ingest_secret: str | None = Header(default=None)):
    _check_auth(x_ingest_secret)

    lead = pipeline.enrich_lead(pipeline.normalize_lead(payload.model_dump()))
    ai_not = await insight.generate_sales_note(lead)
    lead_id, deduped = await db.upsert_lead(lead, ai_not)

    if lead["segment"] in ("Sicak", "Ilik") and not deduped:
        await anyio.to_thread.run_sync(notify.send_lead_mail, lead, ai_not)

    return LeadOut(
        id=lead_id,
        deduped=deduped,
        skor=lead["lead_skoru"],
        segment=lead["segment"],
        asama=lead["asama"],
        takip_tarihi=str(lead["takip_tarihi"]),
    )
