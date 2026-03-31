#!/bin/bash
# MindID NocoDB — Google Cloud VM Kurulum Scripti
# Bu scripti VM'e SSH ile baglanip calistir
# Kullanim: bash setup.sh

set -e
echo "=== MindID NocoDB Kurulumu Basliyor ==="

# 1. Sistem guncelle
echo "[1/5] Sistem guncelleniyor..."
sudo apt update && sudo apt upgrade -y

# 2. Docker kur
echo "[2/5] Docker kuruluyor..."
sudo apt install -y ca-certificates curl gnupg
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# 3. Docker'i root'suz calistir
echo "[3/5] Docker izinleri ayarlaniyor..."
sudo usermod -aG docker $USER

# 4. Proje klasoru olustur
echo "[4/5] Proje klasoru hazirlaniyor..."
mkdir -p ~/mindid-nocodb
cd ~/mindid-nocodb

# 5. .env dosyasi olustur (guclu sifrelerle)
echo "[5/5] Ortam degiskenleri olusturuluyor..."
if [ ! -f .env ]; then
  POSTGRES_PW=$(openssl rand -hex 16)
  JWT_SECRET=$(openssl rand -hex 32)
  cat > .env << EOF
POSTGRES_PASSWORD=${POSTGRES_PW}
JWT_SECRET=${JWT_SECRET}
EOF
  echo ".env dosyasi olusturuldu (sifreler otomatik uretildi)"
  echo "POSTGRES_PASSWORD: ${POSTGRES_PW}"
  echo "JWT_SECRET: ${JWT_SECRET}"
  echo ">>> BU SIFRELERI GUVENLI BIR YERE KAYDET <<<"
else
  echo ".env zaten var, atlanıyor"
fi

echo ""
echo "=== Kurulum Tamamlandi ==="
echo "Simdi docker-compose.yml ve nginx.conf dosyalarini bu klasore kopyala"
echo "Sonra calistir: docker compose up -d"
