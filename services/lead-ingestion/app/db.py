"""PostgreSQL erisimi (asyncpg). UNIQUE(external_id) ile idempotent upsert."""
from __future__ import annotations

import json
import os

import asyncpg

_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(os.environ["DATABASE_URL"], min_size=1, max_size=5)
    return _pool


async def close_pool() -> None:
    global _pool
    if _pool is not None:
        await _pool.close()
        _pool = None


UPSERT_SQL = """
INSERT INTO leads (
    external_id, leadgen_id, kaynak, ad_soyad, email, telefon, sirket_adi,
    sektor, konum, butce, mesaj, lead_skoru, segment, asama,
    pipeline_asamasi, takip_tarihi, ai_satis_notu, source_workflow, raw
) VALUES ($1,$2,$3,$4,$5,$6,$7,$8,$9,$10,$11,$12,$13,$14,$15,$16,$17,$18,$19)
ON CONFLICT (external_id) DO UPDATE SET
    leadgen_id = COALESCE(EXCLUDED.leadgen_id, leads.leadgen_id),
    kaynak = EXCLUDED.kaynak,
    ad_soyad = EXCLUDED.ad_soyad,
    email = COALESCE(EXCLUDED.email, leads.email),
    telefon = COALESCE(EXCLUDED.telefon, leads.telefon),
    sirket_adi = COALESCE(EXCLUDED.sirket_adi, leads.sirket_adi),
    sektor = EXCLUDED.sektor,
    konum = COALESCE(EXCLUDED.konum, leads.konum),
    butce = COALESCE(EXCLUDED.butce, leads.butce),
    mesaj = COALESCE(EXCLUDED.mesaj, leads.mesaj),
    lead_skoru = EXCLUDED.lead_skoru,
    segment = EXCLUDED.segment,
    asama = EXCLUDED.asama,
    pipeline_asamasi = EXCLUDED.pipeline_asamasi,
    takip_tarihi = EXCLUDED.takip_tarihi,
    ai_satis_notu = EXCLUDED.ai_satis_notu,
    raw = EXCLUDED.raw,
    updated_at = now()
RETURNING id, (xmax <> 0) AS deduped
"""


async def upsert_lead(lead: dict, ai_not: str, source_workflow: str = "lead-ingestion-api") -> tuple[int, bool]:
    """Lead'i ekler/gunceller. Doner: (id, deduped)."""
    pool = await get_pool()
    row = await pool.fetchrow(
        UPSERT_SQL,
        lead["external_id"], lead["leadgen_id"], lead["source"], lead["ad_soyad"],
        lead["email"], lead["telefon"], lead["sirket_adi"], lead["sektor"],
        lead["konum"], lead["butce"], lead["mesaj"], lead["lead_skoru"],
        lead["segment"], lead["asama"], lead["pipeline_asamasi"],
        lead["takip_tarihi"], ai_not, source_workflow, json.dumps(lead["raw"], ensure_ascii=False),
    )
    return row["id"], row["deduped"]
