import os
import sys
import platform
import subprocess
import requests
import stat

def setup():
    sys_name = platform.system().lower()
    GITHUB_USER = 'hakan57600'
    home = os.path.expanduser('~')
    
    print(f"\n🌍 HAKAN WORLD v5.1 - UNIVERSAL INSTALLER")

    # 1. WINDOWS ÖZEL: Python Garanti Altına Alınsın
    if 'windows' in sys_name:
        print("🔍 Windows sistemi tespit edildi. Python kontrol ediliyor...")
        try:
            subprocess.run(["python", "--version"], check=True, capture_output=True)
        except:
            print("🐍 Python bulunamadı. winget ile kuruluyor...")
            subprocess.run("winget install -e --id Python.Python.3.11 --silent", shell=True)
            print("✅ Python kurulumu başlatıldı. Lütfen bu pencereyi kapatıp yeni bir terminalde tekrar çalıştırın.")
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

    # 4. brain.py ÇEK
    print("🧠 En güncel zeka indiriliyor...")
    url = f'https://raw.githubusercontent.com/{GITHUB_USER}/hakanbrain/main/brain.py'
    res = requests.get(url)
    brain_path = os.path.join(home, 'brain.py')
    with open(brain_path, 'w', encoding='utf-8') as f:
        f.write(res.text)

    # 5. KOMUTU SİSTEME KAZI
    if 'linux' in sys_name or 'android' in sys_name:
        bin_path = os.path.expanduser('~/.local/bin')
        os.makedirs(bin_path, exist_ok=True)
        hw_file = os.path.join(bin_path, 'hakanworld')
        with open(hw_file, 'w') as f:
            f.write(f'#!/bin/bash\npython3 {brain_path} "$@"\n')
        os.chmod(hw_file, os.stat(hw_file).st_mode | stat.S_IEXEC)
        print(f"✅ 'hakanworld' komutu hazır.")
    
    elif 'windows' in sys_name:
        bat_path = os.path.join(home, 'hakanworld.bat')
        with open(bat_path, 'w') as f:
            f.write(f'@echo off\npython "{brain_path}" %*')
        print(f"✅ Windows için '{bat_path}' hazır. Bu dosyayı PATH'e ekleyebilirsiniz.")

    print("\n🎉 Kurulum bitti! Artık sadece 'hakanworld' yaz.")

if __name__ == "__main__":
    setup()
