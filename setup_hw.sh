#!/bin/bash

# --- 🧠 HW (Hakan World) EVRENSEL KURULUM SCRIPT'İ ---
# Kullanım: curl -sSL [link] | bash

echo "🌟 HW Dağıtık Tomi Kurulumu Başlıyor..."

# 1. Gerekli Sistem Paketleri
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo "📦 Sistem paketleri kontrol ediliyor..."
    sudo apt update -y && sudo apt install -y git python3 python3-pip curl
elif [[ "$OSTYPE" == "darwin"* ]]; then
    echo "📦 MacOS tespiti yapıldı..."
    brew install git python curl
fi

# 2. Ollama (Zeka Katmanı) Kontrolü
if ! command -v ollama &> /dev/null; then
    echo "🧠 Ollama bulunamadı, kuruluyor..."
    curl -fsSL https://ollama.com/install.sh | sh
fi

# 3. Model Hazırlığı
echo "🤖 Zeka modeli (Llama 3.1) çekiliyor (Bu biraz vakit alabilir)..."
ollama pull llama3.1:8b

# 4. Ruhun (GitHub) Klonlanması
if [ ! -d "$HOME/hakanbrain" ]; then
    echo "📂 Ruh (GitHub) klonlanıyor..."
    cd $HOME
    # Token ve User burada kullanıcıdan ilk seferde istenecek şekilde kurgulanabilir
    git clone https://github.com/hakan57600/hakanbrain.git
else
    echo "✅ hakanbrain klasörü zaten mevcut."
fi

# 5. Python Bağımlılıkları
echo "📚 Python kütüphaneleri mühürleniyor..."
pip3 install requests duckduckgo-search --quiet

# 6. Alias (Kısayol) Tanımlama
if ! grep -q "alias hw=" ~/.bashrc; then
    echo "alias hw='python3 ~/hakanbrain/brain.py'" >> ~/.bashrc
    source ~/.bashrc
fi

echo "✅ KURULUM TAMAMLANDI!"
echo "Artık terminale 'hw' yazarak Tomi'yi her yerde uyandırabilirsin, Hakan."
