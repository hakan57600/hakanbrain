import os, sys, platform, subprocess, time

def run(cmd): 
    print(f'⚙️ Çalıştırılıyor: {cmd}')
    return subprocess.run(cmd, shell=True)

def setup():
    sys_name = platform.system().lower()
    print(f'\n🚀 HAKAN BRAIN - MASTER KURULUM SİHİRBAZI [{sys_name.upper()}]')
    print('--------------------------------------------------')

    # 1. Kütüphane Kurulumları
    print('[+] Python kütüphaneleri yükleniyor...')
    run(f'{sys.executable} -m pip install PyGithub requests psutil --quiet')
    
    # 2. İşletim Sistemine Özel Paketler
    if 'linux' in sys_name:
        print('[+] Linux paketleri güncelleniyor...')
        run('sudo apt update && sudo apt install -y git curl python3-pip')
    elif 'windows' in sys_name:
        print('[+] Windows için hazırlık yapılıyor...')
        # Windows'ta paket yönetimi için winget veya doğrudan devam
    
    # 3. Ollama Kurulum Kontrolü
    if run('ollama --version').returncode != 0:
        print('[!] Ollama bulunamadı! Lütfen ollama.com adresinden manuel kurun.')
    else:
        print('[+] Ollama hazır. Model indiriliyor (llama3.2:1b)...')
        run('ollama pull llama3.2:1b')

    # 4. Kişisel Ayarlar (Config)
    config_path = os.path.expanduser('~/.hakan_config')
    if not os.path.exists(config_path):
        user = input('\nGitHub Kullanıcı Adın: ')
        token = input('GitHub Token (ghp_...): ')
        with open(config_path, 'w') as f:
            f.write(f'GITHUB_USER={user}\nGITHUB_TOKEN={token}\n')
        print('✅ Kimlik bilgileri kaydedildi.')

    # 5. Beyin Dosyasını İndir
    print('[+] Ana Beyin (brain.py) GitHub\'dan çekiliyor...')
    import requests
    # Bilgileri tekrar oku
    with open(config_path, 'r') as f:
        lines = f.readlines()
        user = lines[0].split('=')[1].strip()
    
    url = f'https://raw.githubusercontent.com/{user}/hakanbrain/main/brain.py'
    try:
        res = requests.get(url)
        with open('brain.py', 'w', encoding='utf-8') as f:
            f.write(res.text)
        print('✅ brain.py başarıyla indirildi.')
    except:
        print('❌ brain.py indirilemedi! Lütfen interneti kontrol edin.')

    print('\n🎉 TÜM SİSTEM HAZIR! Hoş geldin Hakan.')
    print('--------------------------------------------------')
    print('Başlatmak için: python3 brain.py')

if __name__ == "__main__": setup()
