# OPERATIONS — Hassas Noktalar & Geri Dönüş

> **Yeni Claude session'ı buraya bakacak. Önce bu dosyayı oku.**
> Bu dosya 4 repo (`mind-id`, `mind-agent`, `customer_agent`, `mindid-nocodb`) için ortak operasyon kılavuzudur.

---

## ✅ Stable Geri Dönüş Noktaları

| Tag | Tarih | Durum | Geri dönüş |
|---|---|---|---|
| `stable-2026-05-04` | 2026-05-04 | Image gen + lead query + Late posting **çalışıyor** | `git checkout stable-2026-05-04` |

**3 repo'da aynı tag adı:** mind-id, mind-agent, customer_agent.

### Cloud Run revision karşılığı
- `agents-sdk-api-00024-qtz` (v1.20.7) → `stable-2026-05-04` ile uyumlu
- Önceki çalışan: `agents-sdk-api-00023-df2`, `agents-sdk-api-00022-vs6`

### Hızlı rollback
```bash
git checkout stable-2026-05-04

gcloud run services update-traffic agents-sdk-api \
  --region=us-central1 --project=instagram-post-bot-471518 \
  --to-revisions=agents-sdk-api-00024-qtz=100
```

---

## 📋 BEKLEYEN İŞLER

### 1. Branch protection
- [ ] mind-id main: PR + 1 approval gerek
- [ ] mind-agent main: PR + 1 approval gerek
- [ ] customer_agent main: PR + 1 approval gerek

GitHub web UI: `https://github.com/seymaakrs/<repo>/settings/branches` → "Add ruleset" → main → Require PR + Require 1 approval + Do not allow bypassing.

### 2. CLAUDE.md güncellemesi
- [ ] mind-agent CLAUDE.md → `imageGenerationModel: gemini-2.5-flash-image`, `gpt-5 ASLA` notu ekle
- [ ] mind-id CLAUDE.md → "command-center-canvas yeni özellik" notu, branch protection notu

### 3. Güvenlik temizliği (DÜNDEN)
- [ ] `mind-agent/serviceAccount.json` (2376b) git'ten sil + .gitignore
- [ ] `mind-agent/gcp-service-account.json` (2387b) git'ten sil + .gitignore
- [ ] Eski Google AI key (`AIzaSyDGdNaR...kpM`) AI Studio'dan **silindi mi?** Doğrula
- [ ] Yeni Google AI key (`AIzaSyAf...bx08`) chat'e geçti — **rotate edilmeli**
- [ ] Late/Zernio key (`sk_518334...`) chat'e geçti — rotate öner
- [ ] mind-id PR #6 → `netlify.toml` SECRETS_SCAN_OMIT_KEYS bypass içeriyor → **MERGE EDİLMEMELİ**
- [ ] NocoDB `claude-setup` token revoke
- [ ] n8n `claude-status-2026-05-01` token revoke

### 4. gitleaks (pre-commit secret scanner)
- [ ] 3 repo'ya da kur

### 5. Firestore Security Rules
- [ ] `settings/app_settings` belgesi sadece super_admin yazabilsin

### 6. Şeyma için onay matrisi
- [ ] `CHANGES_REQUIRE_APPROVAL.md` hazırla

### 7. mind-id `/satis` sayfası
- [ ] NocoDB Leadler tablosu read-only dashboard

### 8. Anasayfa Canvas
- [x] command-center-canvas.tsx (4 gün önce merge) ✅
- [ ] Team hierarchy canvas (PR #6, MERGE EDİLMEMELİ — secret bypass içerir)

### 9. Meta Lead Ads webhook
- [ ] Facebook App Review onayı bekleniyor

### 10. Meta agent → sales_agent rename
- [ ] İsim kafa karıştırıcı

### 11. Orchestrator model upgrade
- [ ] gpt-4.1-mini routing'de zayıf, lead bypass var ama gelecekte gpt-4o öneri

---

## 🚨 ASLA YAPMA Listesi

1. ❌ `marketingModel`, `analysisAgent` Firestore'a `gpt-5` yazma → **OpenAI'da gpt-5 YOK**, fake-success döner
2. ❌ `imageGenerationModel`'i `gemini-2.0-flash-image-generation` yapma → Google API'de yok, 404
3. ❌ Repo'ya `serviceAccount.json` / private key commit etme → Google otomatik iptal eder
4. ❌ Netlify secret scan'i bypass etme → güvenlik açığı
5. ❌ Cloud Run revision'a doğrudan deploy etmeden Firestore env'i değiştir → cache uyumsuzluğu
6. ❌ Frontend (mind-id) `serverUrl` Firestore alanını silme → "Bağlantı yok"
7. ❌ Cloud Run servisini `--no-allow-unauthenticated` yapma → mind-id frontend Netlify'dan erişemez
8. ❌ MindID `late_profile_id` Firestore alanını yanlış değer ile değiştir → sync `accounts: []` döner

---

## 🛠️ Hızlı Kurtarma Komutları

### Sistem sağlık testi
```bash
curl -s https://agents-sdk-api-704233028546.us-central1.run.app/health
# Beklenen: {"status":"ok"}
```

### Beklenen Firestore değerler (2026-05-04):
- `serverUrl`: `https://agents-sdk-api-704233028546.us-central1.run.app`
- `orchestratorModel`: `gpt-4.1-mini`
- `marketingModel`: `gpt-4o`
- `analysisAgent`: `gpt-4o`
- `imageGenerationModel`: `gemini-2.5-flash-image`

---

## 🔗 Önemli URL/ID'ler

| Servis | Değer |
|---|---|
| Cloud Run URL | `https://agents-sdk-api-704233028546.us-central1.run.app` |
| GCP project | `instagram-post-bot-471518` (Cloud Run) |
| Firebase project | `mindid-75079` (Firestore + Storage) |
| Production frontend | `https://mindid.netlify.app` |
| MindID business_id | `vPoHKXpvGqdMQzrjN4i4` |
| Slowdays business_id | `ytS8ENQfrGNQ2rdHvei9` |
| MindID Zernio profile_id | `69f4d7e77e906597eb4ebf54` |

---

**Son güncelleme:** 2026-05-04
