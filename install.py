import os, sys, platform, subprocess

def run(cmd): subprocess.run(cmd, shell=True)

def setup():
    sys_name = platform.system().lower()
    print(f'🚀 Hakan Brain Kurulumu Başlıyor... [{sys_name}]')
    
    # Kütüphaneler
    run(f'{sys.executable} -m pip install PyGithub requests psutil --quiet')
    
    # Config oluşturma
    config_path = os.path.expanduser('~/.hakan_config')
    if not os.path.exists(config_path):
        user = input('GitHub Kullanıcı Adın: ')
        token = input('GitHub Token (ghp_...): ')
        with open(config_path, 'w') as f:
            f.write(f'GITHUB_USER={user}\nGITHUB_TOKEN={token}\n')
        print('✅ Config oluşturuldu.')

    # brain.py indir
    import requests
    url = f'https://raw.githubusercontent.com/{user}/hakanbrain/main/brain.py'
    res = requests.get(url)
    with open('brain.py', 'w') as f: f.write(res.text)
    print('✅ brain.py indirildi. Kurulum Tamam!')
    print('\nÇalıştırmak için: python brain.py')

if __name__ == "__main__": setup()
