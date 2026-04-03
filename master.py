import os
import sys
import platform
import subprocess
import requests
import stat

def setup():
    sys_name = platform.system().lower()
    is_android = 'android' in sys_name or os.path.exists('/data/data/com.termux')
    GITHUB_USER = 'hakan57600'
    home = os.path.expanduser('~')
    
    print(f"\n🌍 HAKAN WORLD (HW) v6.0 - BRANDED INSTALLER")

    # 1. WINDOWS ÖZEL: Python Kontrolü
    if 'windows' in sys_name:
        try:
            subprocess.run(["python", "--version"], check=True, capture_output=True)
        except:
            print("🐍 Python bulunamadı. winget ile kuruluyor...")
            subprocess.run("winget install -e --id Python.Python.3.11 --silent", shell=True)
            print("✅ Python kuruldu. Lütfen yeni terminalde tekrar çalıştırın.")
            sys.exit(0)

    # 2. BAĞIMLILIKLAR
    print("📦 Kütüphaneler kuruluyor...")
    subprocess.run([sys.executable, "-m", "pip", "install", "requests", "psutil", "PyGithub", "--quiet"])

    # 3. CONFIG
    config_path = os.path.join(home, '.hakan_config')
    if not os.path.exists(config_path):
        t = input('\n🔑 GitHub Token girin: ')
        with open(config_path, 'w') as f:
            f.write(f'GITHUB_USER={GITHUB_USER}\nGITHUB_TOKEN={t}\n')

    # 4. brain.py İNDİR
    print("🧠 HW Zekası indiriliyor...")
    url = f'https://raw.githubusercontent.com/{GITHUB_USER}/hakanbrain/main/brain.py'
    res = requests.get(url)
    brain_path = os.path.join(home, 'brain.py')
    with open(brain_path, 'w', encoding='utf-8') as f:
        f.write(res.text)

    # 5. KOMUTLARI SİSTEME KAZI (hakanworld & HW)
    if 'linux' in sys_name or is_android:
        bin_path = os.path.expanduser('~/.local/bin')
        os.makedirs(bin_path, exist_ok=True)
        
        # Hem 'hakanworld' hem 'HW' dosyalarını oluştur
        commands = ['hakanworld', 'HW', 'hw']
        for cmd in commands:
            hw_file = os.path.join(bin_path, cmd)
            with open(hw_file, 'w') as f:
                f.write(f'#!/bin/bash\npython3 {brain_path} "$@"\n')
            os.chmod(hw_file, os.stat(hw_file).st_mode | stat.S_IEXEC)
        
        # PATH ve Alias (Yedek olarak)
        rc_path = os.path.join(home, '.bashrc' if not is_android else '../usr/etc/bash.bashrc')
        if os.path.exists(rc_path):
            with open(rc_path, 'a') as f:
                f.write(f'\n# Hakan World Brand\nexport PATH="$HOME/.local/bin:$PATH"\n')
                f.write(f"alias hw='HW'\n")

        print(f"✅ Marka tescillendi: 'hakanworld' ve 'HW' komutları hazır.")
    
    elif 'windows' in sys_name:
        for cmd in ['hakanworld.bat', 'HW.bat', 'hw.bat']:
            bat_path = os.path.join(home, cmd)
            with open(bat_path, 'w') as f:
                f.write(f'@echo off\npython "{brain_path}" %*')
        print(f"✅ Windows Markası: '{home}\\HW.bat' hazır.")

    print("\n🎉 Kurulum bitti! Artık sadece 'HW' yazarak dünyanı başlatabilirsin.")

if __name__ == "__main__":
    setup()
