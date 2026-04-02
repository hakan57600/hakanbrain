import os, sys, platform, subprocess, requests, stat

def run(cmd): subprocess.run(cmd, shell=True)

def setup():
    sys_name = platform.system().lower()
    GITHUB_USER = 'hakan57600'
    print(f'
🌍 HAKAN WORLD MASTER SETUP v4.4')
    
    # 1. Bağımlılıklar
    run(f'{sys.executable} -m pip install PyGithub requests psutil --quiet')
    
    # 2. Config Ayarları
    home = os.path.expanduser('~')
    config_path = os.path.join(home, '.hakan_config')
    if not os.path.exists(config_path):
        t = input('
Lütfen GitHub Token (ghp_...) girin: ')
        with open(config_path, 'w') as f:
            f.write(f'GITHUB_USER={GITHUB_USER}
GITHUB_TOKEN={t}
')
    
    # 3. brain.py İndirme
    url = f'https://raw.githubusercontent.com/{GITHUB_USER}/hakanbrain/main/brain.py'
    res = requests.get(url)
    brain_path = os.path.join(home, 'brain.py')
    with open(brain_path, 'w', encoding='utf-8') as f: f.write(res.text)

    # 4. KESİN ÇÖZÜM: 'hakanworld' ÇALIŞTIRICI DOSYASI OLUŞTURMA
    # Alias yerine doğrudan çalıştırılabilir bir dosya oluşturuyoruz (Anında aktif olur)
    if 'linux' in sys_name or 'android' in sys_name:
        bin_path = os.path.join(home, '.local/bin')
        os.makedirs(bin_path, exist_ok=True)
        hakanworld_script = os.path.join(bin_path, 'hakanworld')
        
        with open(hakanworld_script, 'w') as f:
            f.write(f'#!/bin/bash
python3 {brain_path} ""
')
        
        # Çalıştırma izni ver (chmod +x)
        st = os.stat(hakanworld_script)
        os.chmod(hakanworld_script, st.st_mode | stat.S_IEXEC)
        
        # PATH kontrolü ve alias ekleme (Yedek olarak)
        rc_path = os.path.join(home, '.bashrc')
        with open(rc_path, 'a') as f:
            f.write(f"
export PATH="/home/hakan/miniconda3/bin:/home/hakan/miniconda3/condabin:/home/hakan/.npm-global/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/snap/bin:/home/hakan/.lmstudio/bin:/home/hakan/.local/bin:{bin_path}"
")
            f.write(f"alias hakanworld='python3 {brain_path}'
")
            
        print(f'✅ hakanworld komutu sisteme kazındı.')
    
    elif 'windows' in sys_name:
        bat_path = os.path.join(os.environ['USERPROFILE'], 'hakanworld.bat')
        with open(bat_path, 'w') as f: f.write(f'@python {brain_path} %*')
        print(f'✅ Windows kısayolu hazır.')

    print('
🎉 KURULUM BİTTİ! Artık sadece "hakanworld" yaz.')

if __name__ == "__main__": setup()