import os
import sys
import subprocess
import platform
import psutil
import json

def get_hardware_profile():
    """Cihazın donanım gücünü analiz eder."""
    ram_gb = psutil.virtual_memory().total / (1024**3)
    if ram_gb < 4: return "ZAYIF"
    if ram_gb < 12: return "ORTA"
    return "GUCLU"

def setup():
    print("\n🌍 HW (HAKAN WORLD) - AKILLI OTONOM KURULUMCU")
    home = os.path.expanduser('~')
    profile = get_hardware_profile()
    print(f"🖥️ Donanım Profili: {profile} ({psutil.virtual_memory().total / (1024**3):.1f} GB RAM), Hakan Bey.")

    # 1. Kütüphaneleri kur
    print("📦 Bağımlılıklar mühürleniyor...")
    libs = ["requests", "psutil", "pyttsx3", "gTTS", "duckduckgo-search", "beautifulsoup4", "PyGithub"]
    subprocess.run([sys.executable, "-m", "pip", "install"] + libs + ["--quiet"])

    # 2. Config Otonom Kontrol
    config_path = os.path.join(home, '.hakan_config')
    if not os.path.exists(config_path):
        print("\n🔑 HW Sistemi için GitHub Token gereklidir, Hakan Bey.")
        t = input('Token: ').strip()
        with open(config_path, 'w') as f:
            f.write(f'GITHUB_USER=hakan57600\nGITHUB_TOKEN={t}\n')

    # 3. Ollama ve Model Yönetimi (Otonom & Opsiyonel)
    print("🧠 Zekâ katmanı denetleniyor...")
    ollama_installed = subprocess.run(["which", "ollama"], capture_output=True).returncode == 0
    
    if not ollama_installed:
        print("⚠️ Ollama yüklü değil. Kurulum için: 'curl -fsSL https://ollama.com/install.sh | sh', Hakan Bey.")
    else:
        # Donanıma göre model çek
        if profile == "GUCLU":
            models = ["llama3.1:8b", "llava"]
        elif profile == "ORTA":
            models = ["gemma:2b", "llama3.2:1b"]
        else:
            models = ["llama3.2:1b"]
            
        for m in models:
            print(f"🧬 {m} modeli mühürleniyor (Arka plan)...")
            subprocess.Popen(["ollama", "pull", m], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # 4. Kısayolları oluştur
    if platform.system() == "Linux":
        bin_path = os.path.expanduser('~/.local/bin')
        os.makedirs(bin_path, exist_ok=True)
        hw_cmd = os.path.join(bin_path, 'hw')
        with open(hw_cmd, 'w') as f:
            f.write(f'#!/bin/bash\npython3 {os.getcwd()}/brain.py "$@"\n')
        os.chmod(hw_cmd, 0o755)
        print(f"✅ 'hw' komutu her yerden erişilebilir kılındı, Hakan Bey.")

    print("\n🎉 HW SİSTEMİ HAZIR! Sadece 'hw' yazmanız yeterlidir, Hakan Bey.")

if __name__ == "__main__":
    setup()
