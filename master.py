import os
import sys
import platform
import subprocess
import requests
import stat

def run_cmd(cmd):
    try:
        subprocess.run(cmd, shell=True, check=True)
        return True
    except:
        return False

def install_python_windows():
    print("🐍 Windows üzerinde Python bulunamadı. winget ile kuruluyor...")
    if run_cmd("winget install -e --id Python.Python.3.11"):
        print("✅ Python kuruldu. Lütfen terminali kapatıp tekrar açın veya PATH güncelleyin.")
        return True
    return False

def install_python_linux():
    print("🐍 Linux üzerinde Python/Pip aranıyor...")
    if run_cmd("sudo apt update && sudo apt install -y python3 python3-pip"):
        return True
    # Arch Linux için yedek
    if run_cmd("sudo pacman -Sy --noconfirm python python-pip"):
        return True
    return False

def setup():
    sys_name = platform.system().lower()
    is_android = 'android' in sys_name or os.path.exists('/data/data/com.termux')
    GITHUB_USER = 'hakan57600'
    
    print(f"\n🌍 HAKAN WORLD UNIVERSAL MASTER SETUP v5.0")
    print(f"🖥️ Tespit Edilen Sistem: {sys_name.upper()} {'(ANDROID)' if is_android else ''}")

    # 1. PYTHON KONTROLÜ
    try:
        import platform as _
    except ImportError:
        if 'windows' in sys_name:
            install_python_windows()
            sys.exit(0)
        else:
            install_python_linux()

    # 2. BAĞIMLILIKLARIN KURULUMU
    print("📦 Gerekli kütüphaneler kuruluyor (requests, psutil, PyGithub)...")
    run_cmd(f"{sys.executable} -m pip install requests psutil PyGithub --quiet")

    # 3. CONFIG AYARLARI
    home = os.path.expanduser('~')
    config_path = os.path.join(home, '.hakan_config')
    if not os.path.exists(config_path):
        print("\n🔑 GitHub yapılandırması eksik.")
        t = input('Lütfen GitHub Token (ghp_...) girin: ')
        with open(config_path, 'w') as f:
            f.write(f'GITHUB_USER={GITHUB_USER}\nGITHUB_TOKEN={t}\n')
        print("✅ Yapılandırma kaydedildi.")

    # 4. brain.py İNDİRME
    print("🧠 Zeka dosyası (brain.py) indiriliyor...")
    url = f'https://raw.githubusercontent.com/{GITHUB_USER}/hakanbrain/main/brain.py'
    try:
        res = requests.get(url)
        brain_path = os.path.join(home, 'brain.py')
        with open(brain_path, 'w', encoding='utf-8') as f:
            f.write(res.text)
        print("✅ brain.py başarıyla indirildi.")
    except Exception as e:
        print(f"❌ brain.py indirilemedi: {e}")
        return

    # 5. ÇALIŞTIRICI SCRIPT OLUŞTURMA
    if 'linux' in sys_name or is_android:
        bin_path = os.path.expanduser('~/.local/bin')
        os.makedirs(bin_path, exist_ok=True)
        hakanworld_script = os.path.join(bin_path, 'hakanworld')
        
        with open(hakanworld_script, 'w') as f:
            f.write(f'#!/bin/bash\npython3 {brain_path} "$@"\n')
        
        st = os.stat(hakanworld_script)
        os.chmod(hakanworld_script, st.st_mode | stat.S_IEXEC)
        
        rc_path = os.path.join(home, '.bashrc' if not is_android else '../usr/etc/bash.bashrc')
        if os.path.exists(rc_path):
            with open(rc_path, 'r') as f: content = f.read()
            if bin_path not in content:
                with open(rc_path, 'a') as f:
                    f.write(f'\nexport PATH="$HOME/.local/bin:$PATH"\n')
                    f.write(f"alias hakanworld='python3 {brain_path}'\n")
        
        print(f'✅ hakanworld komutu Linux/Android sistemine kazındı.')
    
    elif 'windows' in sys_name:
        # Windows için hakanworld.bat oluştur
        scripts_dir = os.path.join(os.environ['APPDATA'], 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Python 3.11') # Veya PATH'te olan bir yer
        # Daha güvenli: Kullanıcı ana dizinine atıp PATH'e ekleyelim
        bat_path = os.path.join(home, 'hakanworld.bat')
        with open(bat_path, 'w') as f:
            f.write(f'@echo off\npython "{brain_path}" %*')
        print(f'✅ Windows için hakanworld.bat "{home}" dizininde oluşturuldu.')
        print("💡 İpucu: Bu dizini PATH'e eklersen her yerden çalışır.")

    print("\n🎉 KURULUM TAMAMLANDI!")
    print("👉 'hakanworld' yazarak başlatabilirsin.")
    print("⚠️  Not: Eğer Ollama kurulu değilse, 'ollama serve' komutu için Ollama'yı ayrıca kurman gerekebilir.")

if __name__ == "__main__":
    setup()
