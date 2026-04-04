import os
import sys
import subprocess
import platform

def setup():
    print("\n🌍 HW (HAKAN WORLD) - EVRENSEL KURULUMCU BAŞLATILDI")
    home = os.path.expanduser('~')
    
    # 1. Gerekli kütüphaneleri kur
    print("📦 Bağımlılıklar mühürleniyor...")
    libs = ["requests", "psutil", "pyttsx3", "gTTS", "duckduckgo-search", "beautifulsoup4", "PyGithub"]
    subprocess.run([sys.executable, "-m", "pip", "install"] + libs + ["--quiet"])

    # 2. Config kontrolü
    config_path = os.path.join(home, '.hakan_config')
    if not os.path.exists(config_path):
        print("\n🔑 İlk kurulum: GitHub Token gereklidir, Hakan Bey.")
        t = input('Lütfen GitHub Token girin: ')
        with open(config_path, 'w') as f:
            f.write(f'GITHUB_USER=hakan57600\nGITHUB_TOKEN={t}\n')

    # 3. Kısayolları oluştur (Linux/Termux)
    if platform.system() == "Linux":
        bin_path = os.path.expanduser('~/.local/bin')
        os.makedirs(bin_path, exist_ok=True)
        hw_cmd = os.path.join(bin_path, 'hw')
        with open(hw_cmd, 'w') as f:
            f.write(f'#!/bin/bash\npython3 {os.getcwd()}/brain.py "$@"\n')
        os.chmod(hw_cmd, 0o755)
        print(f"✅ 'hw' komutu sisteme kazındı, Hakan Bey.")

    print("\n🎉 Kurulum Tamamlandı! Artık 'python3 brain.py' veya 'hw' yazarak canlandırabilirsiniz, Hakan Bey.")

if __name__ == "__main__":
    setup()
