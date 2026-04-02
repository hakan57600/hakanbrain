import os, sys, platform, subprocess, requests

def run(cmd): subprocess.run(cmd, shell=True)

def setup():
    sys_name = platform.system().lower()
    print(f'
🌍 HAKAN WORLD KURULUYOR... [{sys_name.upper()}]')
    
    # Kütüphaneler
    run(f'{sys.executable} -m pip install PyGithub requests psutil --quiet')
    
    # Config Bilgileri
    config_path = os.path.expanduser('~/.hakan_config')
    if not os.path.exists(config_path):
        user = input('
GitHub Kullanıcı Adın: ')
        token = input('GitHub Token (ghp_...): ')
        with open(config_path, 'w') as f:
            f.write(f'GITHUB_USER={user}
GITHUB_TOKEN={token}
')

    # brain.py İndir
    with open(config_path, 'r') as f:
        user = f.readlines()[0].split('=')[1].strip()
    
    url = f'https://raw.githubusercontent.com/{user}/hakanbrain/main/brain.py'
    res = requests.get(url)
    brain_path = os.path.join(os.path.expanduser('~'), 'brain.py')
    with open(brain_path, 'w', encoding='utf-8') as f: f.write(res.text)

    # hakanworld KISAYOLU (Alias)
    home = os.path.expanduser('~')
    if 'linux' in sys_name or 'android' in sys_name:
        rc_path = os.path.join(home, '.bashrc')
        alias_cmd = f"
alias hakanworld='python3 {brain_path}'
"
        with open(rc_path, 'a') as f: f.write(alias_cmd)
        print('✅ hakanworld komutu sisteme eklendi! (Terminali kapatıp açın)')
    elif 'windows' in sys_name:
        bat_path = os.path.join(home, 'hakanworld.bat')
        with open(bat_path, 'w') as f: f.write(f'@python {brain_path} %*')
        print(f'✅ hakanworld.bat oluşturuldu: {bat_path}')

    print('
🎉 Kurulum Bitti! Artık sadece "hakanworld" yazman yeterli.')

if __name__ == '__main__': setup()