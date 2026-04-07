#!/bin/bash

echo "🌍 HW (HAKAN WORLD) - EVRENSEL KURULUMCU V3.0"
echo "------------------------------------------"

# 1. Bağımlılıkları Kur
echo "📦 Bağımlılıklar denetleniyor..."
pip install requests duckduckgo-search --quiet

# 2. 'hw' komutunu mühürle
echo "🔑 'hw' komutu mühürleniyor..."
BRAIN_PATH="/home/hakan/hakanbrain/brain.py"

# Eğer dosya varsa devam et
if [ -f "$BRAIN_PATH" ]; then
    echo -e "#!/bin/bash\npython3 $BRAIN_PATH \"\$@\"" | sudo tee /usr/local/bin/hw > /dev/null
    sudo chmod +x /usr/local/bin/hw
    echo "✅ 'hw' komutu artık emrinde!"
else
    echo "⚠️ brain.py bulunamadı! Lütfen dizini kontrol et."
fi

# 3. GitHub kontrolü
echo "📡 GitHub senkronizasyonu hazır mı?"
if [ -d ".git" ]; then
    echo "✅ Git deposu aktif."
else
    echo "⚠️ Git deposu bulunamadı. Lütfen 'git init' ve 'git remote add origin ...' işlemlerini yap."
fi

echo "------------------------------------------"
echo "🎉 Tomi v17.0 Kurulumu Tamamlandı, Hakan!"
