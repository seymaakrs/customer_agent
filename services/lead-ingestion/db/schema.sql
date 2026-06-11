-- Lead Ingestion semasi (Faz 1) — PostgreSQL
-- Idempotency DB seviyesinde gercek UNIQUE index'lerle garanti edilir.

CREATE TABLE IF NOT EXISTS leads (
    id                BIGSERIAL PRIMARY KEY,
    external_id       TEXT NOT NULL,
    leadgen_id        TEXT,
    kaynak            TEXT NOT NULL,            -- Site | Meta Ads | WhatsApp | IG DM | LinkedIn | Clay | Manuel
    ad_soyad          TEXT NOT NULL,
    email             TEXT,
    telefon           TEXT,                     -- E.164 (+90...)
    sirket_adi        TEXT,
    sektor            TEXT NOT NULL DEFAULT 'Diger',
    konum             TEXT,
    butce             INTEGER,
    mesaj             TEXT,
    lead_skoru        INTEGER NOT NULL DEFAULT 0 CHECK (lead_skoru BETWEEN 0 AND 100),
    segment           TEXT NOT NULL,            -- Sicak | Ilik | Soguk | Nurture
    asama             TEXT NOT NULL DEFAULT 'Yeni',  -- Yeni | Ilik | Sicak | Soguk | Teklif | Kazanildi | Kayip
    pipeline_asamasi  TEXT NOT NULL DEFAULT 'takip',
    takip_tarihi      DATE,
    ai_satis_notu     TEXT,
    source_workflow   TEXT,
    raw               JSONB NOT NULL DEFAULT '{}'::jsonb,
    created_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
    CONSTRAINT leads_external_id_key UNIQUE (external_id)
);

CREATE UNIQUE INDEX IF NOT EXISTS leads_leadgen_id_key
    ON leads (leadgen_id) WHERE leadgen_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS leads_takip_tarihi_idx ON leads (takip_tarihi);
CREATE INDEX IF NOT EXISTS leads_segment_idx ON leads (segment);

CREATE TABLE IF NOT EXISTS etkilesimler (
    id                   BIGSERIAL PRIMARY KEY,
    lead_id              BIGINT NOT NULL REFERENCES leads(id) ON DELETE CASCADE,
    external_message_id  TEXT,
    kanal                TEXT,                  -- Meta Form | WhatsApp | IG DM | Email | ...
    yon                  TEXT,                  -- Gelen | Giden
    tur                  TEXT,                  -- Ilk Mesaj | Takip Mesaji | ...
    mesaj_icerigi        TEXT,
    created_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE UNIQUE INDEX IF NOT EXISTS etkilesimler_external_message_id_key
    ON etkilesimler (external_message_id) WHERE external_message_id IS NOT NULL;

CREATE INDEX IF NOT EXISTS etkilesimler_lead_id_idx ON etkilesimler (lead_id);

-- Ileride AI memory / semantic search icin (Neon pgvector destekler).
-- Ihtiyac dogdugunda ac:
-- CREATE EXTENSION IF NOT EXISTS vector;
-- ALTER TABLE leads ADD COLUMN IF NOT EXISTS embedding vector(1536);
