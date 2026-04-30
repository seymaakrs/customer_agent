# n8n Workflow JSON Exports

Bu dizin, **n8n Cloud**'da tanımlı satış workflow'larının JSON export'larını version control altında tutar.

## Neden burada?

Field mapping'ler n8n UI'da elle yapılıyor ve **kod review'a girmiyor**. Bir kolon adı değişirse 5 workflow sessizce bozulur. Bu dizin o sessiz drift'i kırar:

- Workflow değiştirildiğinde JSON'u export et → bu dizine commit et
- PR diff'inde mapping değişikliği görünür hale gelir
- Geri dönüş için cold backup

## Workflow ID listesi

| Dosya | Workflow ID | n8n Adı | Durum |
|---|---|---|---|
| `meta-lead-ads-agent.json` | xblguxS49CJ4r4OF | Meta Lead Ads Agent | PAUSED (App Review) |
| `lead-toplama-agent.json` | l31p16NRZeyk4eEm | Lead Toplama Agent | ACTIVE |
| `takip-agent.json` | nWNMQYHJzsMvMUGP | Takip Agent | ACTIVE |
| `itiraz-agent.json` | 9nTdKNPLCjo8DKfE | İtiraz Agent | ACTIVE |
| `upsell-agent.json` | kVXXr4e6O5F3lGiD | Upsell Agent | ACTIVE |

## Export nasıl yapılır

n8n Cloud UI:
1. Workflow'u aç → ⋯ (3-dot menu) → **Download** → JSON dosyası iner
2. Bu dizine kopyala (yukarıdaki dosya adıyla)
3. **Credential ID'lerini script ile temizle** (gizli bilgi sızmasın):
   ```bash
   # Örnek: credential ref'lerini placeholder'a çevir
   sed -i 's/"credentialId": "[^"]*"/"credentialId": "REDACTED"/g' *.json
   ```
4. PR aç → reviewer field mapping'in `customer_agent/docs/NOCODB-SCHEMA-V2.md` ile uyumunu doğrular
5. Merge → kayıt güncel

## İlk export ne zaman?

Aktivasyondan **hemen sonra**, ilk smoke test yeşil olduğunda. O an workflow'lar "altın hali" — bunu git'e dondur.

## Şema değişikliği akışı

NocoDB'de bir kolon adı değişirse:
1. `customer_agent/docs/NOCODB-SCHEMA-V2.md` güncelle
2. `mind-agent/tests/test_nocodb_schema_contract.py` beklenen listeyi güncelle
3. n8n Cloud UI'da etkilenen workflow'ların "Save to NocoDB" node'unda mapping'i düzelt
4. Workflow'ları yeniden export et → bu dizine commit et
5. CI: contract test yeşil olana kadar merge'leme

## Güvenlik

- API token, credential ID, webhook URL, OpenAI key gibi alanları **export öncesi** redact et.
- `.gitignore` ek olarak `*.local.json` ekleyebilir — geliştirici lokal kopyaları için.
