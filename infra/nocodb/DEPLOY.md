# MindID NocoDB — Self-Host Deployment

## Gereksinimler
- Google Cloud hesabi (free tier)
- Domain: nocodb.mindid.shop (DNS ayarlanmis)
- GitHub: seymaakrs/mindid-nocodb (fork)

---

## Hizli Kurulum

### 1. Google Cloud VM Olustur
```
Compute Engine → Create Instance
- Name: mindid-nocodb
- Region: us-east1 (free tier)
- Machine type: e2-micro (1 vCPU, 1GB RAM)
- OS: Ubuntu 22.04 LTS
- Boot disk: 30GB (free tier max)
- Firewall: HTTP + HTTPS trafigine izin ver
```

### 2. VM'e Baglan ve Kur
```bash
# SSH ile baglan (Google Cloud Console'dan veya terminal'den)
gcloud compute ssh mindid-nocodb

# Setup scriptini indir ve calistir
curl -o setup.sh https://raw.githubusercontent.com/seymaakrs/mindid-nocodb/main/infra/setup.sh
bash setup.sh

# Yeniden giris yap (docker izinleri icin)
exit
gcloud compute ssh mindid-nocodb
```

### 3. Dosyalari Kopyala ve Calistir
```bash
cd ~/mindid-nocodb

# docker-compose.yml, nginx.conf dosyalarini kopyala
# (GitHub'dan veya scp ile)

# Calistir
docker compose up -d

# Kontrol et
docker compose ps
```

### 4. DNS Ayarla
```
mindid.shop DNS yonetim panelinde:
- A kaydi ekle: nocodb.mindid.shop → VM_IP_ADRESI
```

### 5. SSL Sertifikasi (DNS yayildiktan sonra)
```bash
# Certbot ile SSL al
docker compose run --rm certbot certonly \
  --webroot \
  --webroot-path=/var/lib/letsencrypt \
  -d nocodb.mindid.shop \
  --email seyma@mindid.shop \
  --agree-tos

# nginx.conf'u SSL versiyonuyla degistir
cp nginx-ssl.conf nginx.conf
docker compose restart nginx
```

### 6. n8n Entegrasyonu
```
1. nocodb.mindid.shop'a giris yap
2. Sol alt: Team & Settings → API Tokens → Create
3. n8n'de: Settings → Credentials → NocoDB API
   - Host: https://nocodb.mindid.shop
   - API Token: yukarida olusan token
4. Test: n8n workflow'unda NocoDB node ekle, baglanti test et
```

---

## Kullanici Rolleri
| Kullanici | Rol | Yetki |
|-----------|-----|-------|
| Seyma | Owner | Tam yetki |
| Beyza | Owner | Tam yetki |
| Burak | Editor | Veri okuma/yazma, tablo duzenleme |

---

## Yedekleme
```bash
# Gunluk otomatik yedekleme (crontab -e ile ekle)
0 3 * * * docker exec mindid-nocodb-db pg_dump -U nocodb nocodb > ~/backups/nocodb_$(date +\%Y\%m\%d).sql
```

---

## Dosya Yapisi
```
infra/nocodb/
├── docker-compose.yml     # Ana servis tanimlamasi
├── nginx.conf             # HTTP proxy (baslangic)
├── nginx-ssl.conf         # HTTPS proxy (SSL sonrasi)
├── setup.sh               # VM ilk kurulum scripti
├── .env.example           # Ortam degiskenleri ornegi
└── DEPLOY.md              # Bu dosya
```
