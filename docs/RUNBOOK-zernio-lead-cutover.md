# RUNBOOK — Lead Toplama: n8n → mind-agent Zernio Webhook Geçişi

**Karar (2026-05-19):** Lead toplama akışı n8n "Lead Toplama Agent"tan
çıkarılıp mind-agent'ın kendi Zernio webhook'una alınıyor. n8n diğer
workflow'lar için kalmaya devam ediyor (abonelik durmuyor).

## Mimari (kim ne yapıyor)

| Rol | Bileşen | Görev | LLM? |
|---|---|---|---|
| Beyin | mind-agent (Cloud Run) | Karar verir, mesaj yazar (Claude) | Evet |
| Eller | Zernio | WhatsApp/IG mesaj gönder-al, reklam | Hayır |
| Hafıza | NocoDB | Lead/mesaj kayıtları | Hayır |
| Tesisat | n8n | Düz kural/otomasyon, diğer 10+ workflow | Hayır |
| Yüz | mind-id (Vercel) | Portal/sohbet arayüzü | Hayır |

Lead toplama artık: `Zernio → POST /zernio/webhook (mind-agent) → NocoDB`.
n8n bu akıştan çıkıyor. Kod `mind-agent` `main`'de canlı
(`src/app/zernio_webhook.py`, `api.py`'de `/zernio/webhook` route'una bağlı).
Idempotent (`external_id`), skor formülü eski n8n ile birebir aynı.

## Kullanıcı görevleri (panel — kodda değil)

1. **NocoDB:** `Leadler` tablosu → `kaynak` SingleSelect → option ekle:
   `WhatsApp`. (Yoksa NocoDB 422 döner.)
2. **mind-agent Cloud Run env** dolu olmalı:
   `NOCODB_BASE_URL`, `NOCODB_API_TOKEN`, `NOCODB_LEADS_TABLE_ID`,
   `NOCODB_MESSAGES_TABLE_ID`, `ZERNIO_WEBHOOK_SECRET`.
3. **Zernio dashboard:** Inbox webhook URL'ini
   `https://<mind-agent-cloud-run-url>/zernio/webhook` yap; aynı secret'ı
   `ZERNIO_WEBHOOK_SECRET` ile eşle.
4. **Test:** Test telefonundan WhatsApp mesajı → NocoDB `Leadler`'de tek
   satır (kaynak=WhatsApp, doğru skor, notlar=metin). Tekrar mesaj →
   yeni satır OLUŞMAMALI (idempotency doğrulaması).
5. **Geçiş çalışınca haber ver** → temizlik (aşağısı).

## Geçiş doğrulanınca yapılacak temizlik (Claude tarafı)

- customer_agent **PR #9** (n8n payload fix) → kapat: yol terk edildi.
- customer_agent **PR #10** → n8n fix kısmı geçersiz; devir notlarını
  güncelle.
- n8n "Lead Toplama Agent" workflow'unu **pasife al** (silme — geri
  dönülebilir kalsın).

## Rollback

Sorun çıkarsa: Zernio webhook URL'ini eski n8n adresine geri çevir;
n8n workflow'u zaten pasife alınmadıysa anında devreye girer. Kod
değişikliği gerekmez.
