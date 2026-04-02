import os, sys, platform, subprocess, requests

def run(cmd): return subprocess.run(cmd, shell=True)

def setup():
    sys_name = platform.system().lower()
    print(f"\n🌍 HAKAN WORLD KURULUYOR... [{sys_name.upper()}]")
    
    # Kütüphaneler
    print("[+] Kütüphaneler yükleniyor...")
    run(f"{sys.executable} -m pip install PyGithub requests psutil --quiet")
    
    # Config Bilgileri
    config_path = os.path.expanduser("~/.hakan_config")
    if not os.path.exists(config_path):
        u = input("\nGitHub Kullanıcı Adın: ")
        t = input("GitHub Token (ghp_...): ")
        with open(config_path, "w") as f:
            f.write(f"GITHUB_USER={u}\nGITHUB_TOKEN={t}\n")

    # Config'den kullanıcıyı oku
    if not os.path.exists(config_path):
        print("❌ Hata: Ayar dosyası oluşturulamadı.")
        return

    with open(config_path, "r") as f:
        lines = f.readlines()
        user_lines = [l for l in lines if "USER=" in l]
        if not user_lines:
            print("❌ Hata: Config dosyasında USER bulunamadı.")
            return
        u = user_lines[0].split("=")[1].strip()

    # brain.py İndir
    print(f"[+] Beyin indiriliyor (User: {u})...")
    url = f"https://raw.githubusercontent.com/{u}/hakanbrain/main/brain.py"
    try:
        res = requests.get(url)
        if res.status_code == 200:
            home = os.path.expanduser("~")
            brain_path = os.path.join(home, "brain.py")
            with open(brain_path, "w", encoding="utf-8") as f: f.write(res.text)
            print("✅ brain.py başarıyla indirildi.")
            
            # hakanworld KISAYOLU (Alias)
            if "linux" in sys_name or "android" in sys_name:
                rc_path = os.path.join(home, ".bashrc")
                alias_cmd = f"\nalias hakanworld='python3 {brain_path}'\n"
                # Varsa tekrar ekleme
                try:
                    with open(rc_path, "r") as f: content = f.read()
                except: content = ""
                
                if "alias hakanworld" not in content:
                    with open(rc_path, "a") as f: f.write(alias_cmd)
                    print("✅ hakanworld komutu sisteme eklendi!")
                else:
                    print("ℹ️ hakanworld zaten sisteme kayıtlı.")
            elif "windows" in sys_name:
                bat_path = os.path.join(home, "hakanworld.bat")
                with open(bat_path, "w") as f: f.write(f"@python {brain_path} %*")
                print(f"✅ hakanworld.bat oluşturuldu.")
        else:
            print(f"❌ Hata: brain.py indirilemedi (HTTP {res.status_code})")
    except Exception as e:
        print(f"❌ İndirme hatası: {e}")

    print("\n🎉 Kurulum Bitti! Artık sadece 'hakanworld' yazman yeterli.")

if __name__ == "__main__": setup()
