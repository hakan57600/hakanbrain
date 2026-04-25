#!/bin/bash
# HAKAN BRAIN - AKILLI KURULUM MOTORU (Linux & Android)

echo "------------------------------------------"
echo "   HAKAN BRAIN v8.7 BOOTSTRAP MOTORU      "
echo "------------------------------------------"

# 1. Platform Tespiti ve Temel Araçların Kurulumu
if [ -d "/data/data/com.termux" ]; then
    OS="Android"
    PM="pkg"
    INSTALL_CMD="pkg install -y"
    echo "[!] Termux ortamı tespit edildi."
else
    OS="Linux"
    PM="apt"
    INSTALL_CMD="sudo apt install -y"
    echo "[!] Linux (Debian/Ubuntu) ortamı tespit edildi."
fi

# 2. Kritik Bağımlılık Kontrolü (Git, Python, Pip)
check_and_install() {
    if ! command -v $1 &> /dev/null; then
        echo "[+] $1 eksik, kuruluyor..."
        $INSTALL_CMD $2
    else
        echo "[ok] $1 zaten yüklü."
    fi
}

if [ "$OS" == "Linux" ]; then
    sudo apt update
fi

check_and_install git git
check_and_install python3 python3
check_and_install pip3 python3-pip

# 3. Proje Klasörü ve Git İşlemleri
if [ ! -d "hakanbrain" ]; then
    echo "[+] Proje indiriliyor (GitHub)..."
    git clone https://github.com/hakan57600/hakanbrain.git
    cd hakanbrain
else
    echo "[+] Mevcut klasör bulundu, güncelleniyor..."
    cd hakanbrain
    git pull
fi

# 4. Python Kütüphaneleri (Sanal Ortam veya Global)
echo "[+] Python kütüphaneleri optimize ediliyor..."
pip3 install requests psutil --break-system-packages 2>/dev/null || pip3 install requests psutil

# 5. Konfigürasyon Kurtarma
if [ ! -f "config.json" ]; then
    echo "[!] config.json oluşturuluyor..."
    echo '{
    "GITHUB_TOKEN": "BURAYA_GITHUB_TOKEN_GIRIN",
    "GITHUB_REPO": "hakan57600/hakanbrain",
    "GROQ_API_KEY": "BURAYA_ANAHTAR_GIRIN",
    "DEVICE_NAME": "Yeni Cihaz"
}' > config.json
fi

echo "------------------------------------------"
echo "   KURULUM BAŞARILI! (Cihaz: $OS)         "
echo "   Komut: python3 kollar.py               "
echo "------------------------------------------"
