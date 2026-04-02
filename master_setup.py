import os, sys, platform, subprocess, requests

def run(cmd): subprocess.run(cmd, shell=True)

def setup():
    sys_name = platform.system().lower()
    GITHUB_USER = 'hakan57600'
    
    print(f'
🌍 HAKAN WORLD MASTER SETUP v4.2 [User: {GITHUB_USER}]')
    
    # Kütüphaneler
    run(f'{sys.executable} -m pip install PyGithub requests psutil --quiet')
    
    # Config Ayarları
    config_path = os.path.expanduser('~/.hakan_config')
    if not os.path.exists(config_path):
        t = input('
Lütfen GitHub Token (ghp_...) girin: ')
        with open(config_path, 'w') as f:
            f.write(f'GITHUB_USER={GITHUB_USER}
GITHUB_TOKEN={t}
')
    
    # brain.py İndirme
    url = f'https://raw.githubusercontent.com/{GITHUB_USER}/hakanbrain/main/brain.py'
    try:
        res = requests.get(url)
        if res.status_code == 200:
            home = os.path.expanduser('~')
            brain_path = os.path.join(home, 'brain.py')
            with open(brain_path, 'w', encoding='utf-8') as f: f.write(res.text)
            
            # Alias (Kısayol)
            if 'linux' in sys_name or 'android' in sys_name:
                rc_path = os.path.join(home, '.bashrc')
                alias_cmd = f"
alias hakanworld='python3 {brain_path}'
"
                try:
                    with open(rc_path, 'r') as fr: content = fr.read()
                except: content = ''
                if 'alias hakanworld' not in content:
                    with open(rc_path, 'a') as fa: fa.write(alias_cmd)
                    print('✅ hakanworld komutu eklendi!')
            elif 'windows' in sys_name:
                bat_path = os.path.join(home, 'hakanworld.bat')
                with open(bat_path, 'w') as f: f.write(f'@python {brain_path} %*')
                print(f'✅ hakanworld.bat oluşturuldu.')
        else:
            print(f'❌ Hata: brain.py indirilemedi (HTTP {res.status_code})')
    except Exception as e:
        print(f'❌ Bağlantı hatası: {e}')

    print('
🎉 Kurulum Tamamlandı! Artık sadece "hakanworld" yazman yeterli.')

if __name__ == "__main__": setup()