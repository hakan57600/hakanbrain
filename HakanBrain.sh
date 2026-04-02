#!/bin/bash
# Hakan Brain - Linux/Android Calistirici
echo "--------------------------------------------------"
echo "          🚀 HAKAN BRAIN BASLATILIYOR...          "
echo "--------------------------------------------------"

# 1. Python Kontrolü
if ! command -v python3 &> /dev/null
then
    echo "[!] Python3 bulunamadi! Kurulum yapiliyor..."
    if command -v pkg &> /dev/null; then pkg install python -y; else sudo apt install python3 -y; fi
fi

# 2. Beyin Dosyası Güncelleme (GitHub'dan En Son Halini Çek)
TOKEN="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"
echo "[+] Merkez (GitHub) ile senkronize olunuyor..."
curl -H "Authorization: token $TOKEN" -H "Accept: application/vnd.github.v3.raw" -L "https://api.github.com/repos/Hakan57600/hakanbrain/contents/brain.py" -o "brain.py"

# 3. Kütüphane Kontrolü
pip3 install requests psutil --quiet

# 4. Beyni Başlat
echo "[+] Beyin Aktif!"
python3 brain.py

echo "--------------------------------------------------"
echo "✅ Islem Tamamlandi. Kapatmak icin bir tusa basin."
read -n 1
