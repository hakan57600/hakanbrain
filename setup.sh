#!/bin/bash

echo "🌍 HW (HAKAN WORLD) - EVRENSEL KURULUMCU V5.1"
echo "------------------------------------------"

# 1. Token Kontrolü
if [ -z "$GH_TOKEN" ]; then
    echo "⚠️ GITHUB_TOKEN eksik. Lütfen kurulum komutunu şu şekilde çalıştırın:"
    echo "GH_TOKEN=token_buraya curl ... | bash"
    exit 1
fi

# 2. İşletim Sistemi ve Paket Yöneticisi Tespiti
if [ -d "/data/data/com.termux" ]; then
    PKG_MGR="pkg"
    INSTALL_CMD="install -y"
elif command -v apt &> /dev/null; then
    PKG_MGR="sudo apt"
    INSTALL_CMD="install -y"
elif command -v pacman &> /dev/null; then
    PKG_MGR="sudo pacman"
    INSTALL_CMD="-S --noconfirm"
else
    PKG_MGR=""
fi

# 3. Git ve Python Kontrolü
for cmd in git python3; do
    if ! command -v $cmd &> /dev/null; then
        echo "📦 $cmd bulunamadı, kuruluyor..."
        $PKG_MGR $INSTALL_CMD $cmd
    fi
done

PYTHON_CMD="python3"
if ! command -v python3 &> /dev/null; then PYTHON_CMD="python"; fi

# 4. Bağımlılıklar
echo "📦 Bağımlılıklar kuruluyor..."
$PYTHON_CMD -m pip install requests duckduckgo-search --quiet

# 5. Depo Klonlama
TARGET_DIR="$HOME/hakanbrain"
if [ ! -d "$TARGET_DIR/.git" ]; then
    echo "📡 Depo klonlanıyor..."
    git clone https://hakan57600:$GH_TOKEN@github.com/hakan57600/hakanbrain.git "$TARGET_DIR"
    cd "$TARGET_DIR"
fi

# 6. 'hw' Mühürü
BRAIN_PATH="$TARGET_DIR/brain.py"
BIN_DIR="/usr/local/bin"
[ -d "/data/data/com.termux" ] && BIN_DIR="/data/data/com.termux/files/usr/bin"
[ ! -w "$BIN_DIR" ] && BIN_DIR="$HOME/.local/bin" && mkdir -p "$BIN_DIR"

HW_CMD_PATH="$BIN_DIR/hw"
echo "🔑 'hw' mühürleniyor: $HW_CMD_PATH"
echo -e "#!/bin/bash\nGH_TOKEN=$GH_TOKEN python3 $BRAIN_PATH \"\$@\"" | sudo tee "$HW_CMD_PATH" > /dev/null || echo -e "#!/bin/bash\nGH_TOKEN=$GH_TOKEN python3 $BRAIN_PATH \"\$@\"" > "$HW_CMD_PATH"
chmod +x "$HW_CMD_PATH"

echo "✅ Kurulum Tamamlandı!"
