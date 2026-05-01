# Mimari Diyagram — Veritabanı Sınırları ve Veri Akışı

**Tarih:** 2026-04-30
**Bağlam:** ADR-001 ve NOCODB-SCHEMA-V2 ile birlikte okuyun.

---

## 1. Yüksek Seviye — Veritabanı Sınırları

```mermaid
flowchart LR
    subgraph EXT[Dış Kaynaklar]
        META[Meta Lead Ads]
        IG[Instagram DM]
        WA[WhatsApp]
        WEB[Web Form / Webhook]
    end

    subgraph N8N[n8n Cloud — Orchestrator]
        W1[Meta Lead Ads Agent]
        W2[Lead Toplama Agent]
        W3[Takip Agent]
        W4[Itiraz Agent]
        W5[Upsell Agent]
    end

    subgraph NOCO[(NocoDB — CRM SoT)]
        T1[leads]
        T2[lead_messages]
        T3[seyma_notifications]
    end

    subgraph MA[mind-agent — Python Backend]
        NC[nocodb_client]
        FC[firebase_client]
        AG[agents]
    end

    subgraph FB[(Firestore — Media/Ops)]
        F1[businesses/media]
        F2[instagram_stats]
        F3[errors / threads]
    end

    subgraph MID[mind-id — Next.js Portal]
        SAT["/satis tab"]
    end

    META --> W1
    IG --> W2
    WA --> W3
    WEB --> W2

    W1 -- upsert external_id --> T1
    W2 -- upsert external_id --> T1
    W3 -- insert --> T2
    W4 -- insert --> T2
    W5 -- update stage --> T1
    W1 & W2 & W3 & W4 & W5 -- insert --> T3

    AG --> NC
    NC <-- read+write --> NOCO
    AG --> FC
    FC <-- read+write --> FB

    SAT -- read-only --> NC

    classDef sot fill:#1f6feb,stroke:#0b3d91,color:#fff
    classDef ops fill:#6b21a8,stroke:#3b0764,color:#fff
    classDef block fill:#0f766e,stroke:#064e3b,color:#fff
    class NOCO sot
    class FB ops
    class N8N,MA,MID block
```

**Altın kural:** Mavi blok (NocoDB) **CRM source of truth**. Mor blok (Firestore) **medya / operasyonel state**. Bir entity sadece bir blokta yaşar.

---

## 2. Idempotent Yazma Akışı (Lead Upsert)

```mermaid
sequenceDiagram
    participant M as Meta Webhook
    participant N as n8n Workflow
    participant DB as NocoDB /leads
    participant S as seyma_notifications

    M->>N: leadgen_id=L123 (retry olabilir)
    N->>DB: GET /records?where=(leadgen_id,eq,L123)
    alt Kayıt yok
        N->>DB: POST {external_id, leadgen_id, source, ...}
        DB-->>N: 201 Created
    else Kayıt var
        N->>DB: PATCH /records/{id} updated_at=now()
        DB-->>N: 200 OK
    end
    Note over DB: UNIQUE(leadgen_id) duplicate'i DB tarafında da engeller
    N->>S: INSERT kind=hot_lead (score>=80 ise)
```

---

## 3. Bu Oturumda Yapılanlar — Akış Şeması

```mermaid
flowchart TD
    A[Başlangıç: kullanıcı 'veritabanı kontrolü' istedi] --> B[Supabase projeleri keşfedildi - INACTIVE]
    B --> C[Kullanıcı: gerçek DB NocoDB-Firebase, Supabase değil]
    C --> D[Explore agent: 3 repo NocoDB-n8n entegrasyon denetimi]
    D --> E{Bulgular}
    E --> E1[P0-1 Firebase-NocoDB dualism]
    E --> E2[P0-2 NocoDB client main'de yok]
    E --> E3[P0-3 Idempotency yok]
    E --> E4[P1 audit kolonu, token, contract test eksik]

    E1 & E2 & E3 & E4 --> F[Çözüm dosyaları üretildi]

    F --> F1[customer_agent/docs/NOCODB-SCHEMA-V2.md]
    F --> F2[customer_agent/docs/ADR-001-database-boundaries.md]
    F --> F3[customer_agent/docs/INTEGRATION-AUDIT-2026-04-30.md]
    F --> F4[customer_agent/docs/ARCHITECTURE-DIAGRAM.md - bu dosya]
    F --> F5[mind-agent/tests/test_nocodb_schema_contract.py]

    F1 & F2 & F3 & F4 & F5 --> G[Commit + Push: claude/database-integrity-check-6PitF]
    G --> H[Draft PR'lar açıldı]
    H --> I[Kullanıcı aktivasyon adımlarına geçebilir]

    classDef done fill:#16a34a,stroke:#14532d,color:#fff
    classDef issue fill:#dc2626,stroke:#7f1d1d,color:#fff
    class F1,F2,F3,F4,F5,G,H,I done
    class E1,E2,E3,E4 issue
```

---

## 4. Repo Sorumluluk Matrisi

| Repo | Rol | Yazdığı DB | Okuduğu DB |
|---|---|---|---|
| **customer_agent** | Mimari + dokümantasyon | — | — |
| **mind-agent** | Agent backend (Python) | NocoDB (CRM via `nocodb_client`) · Firestore (medya/ops via `firebase_client`) | İkisi de |
| **mind-id** | Next.js portal (`/satis`) | — (read-only) | NocoDB (read token) |
| **n8n** | Workflow orchestrator | NocoDB (CRM) | NocoDB (lookup için) |

---

## 5. Aktivasyon Sırası (DEVİR notu ile uyumlu)

```mermaid
flowchart LR
    S1[1. Bu PR merge - schema + ADR + test] --> S2[2. NocoDB UI'da migration]
    S2 --> S3[3. mind-agent NocoDB client PR merge - PR check-facebook-meta-ads-KM4MZ]
    S3 --> S4[4. Contract test YEŞIL]
    S4 --> S5[5. .env.sales gerçek değerleri]
    S5 --> S6[6. Zernio Inbox addon + webhook]
    S6 --> S7[7. mind-id /satis E2E test]
    S7 --> S8[8. Meta Lead Ads ACTIVE - App Review sonrası]
```

Her adım bir öncekine bağımlıdır — atlamayın. Adım 4 **kırmızı kalırsa** sonraki adımlara geçmeyin: kırık şema = sessiz veri kaybı.
