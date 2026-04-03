import os
import json
import platform
import subprocess
import requests
import sys
import psutil
import time
import datetime
from github import Github, Auth

# --- AYARLAR ---
CONFIG_FILE = os.path.expanduser("~/.hakan_config")
MEMORY_FILE = os.path.expanduser("~/memory.json")
OLLAMA_URL = "http://localhost:11434/api/generate"

class HakanBrain:
    def __init__(self):
        self.token, self.user = self.load_config()
        self.repo_name = f"{self.user}/hakanbrain"
        self.system = platform.system()
        self.ram = psutil.virtual_memory().total / (1024**3)
        # Daha detaylı CPU bilgisi alalım
        try:
            self.cpu = subprocess.check_output("cat /proc/cpuinfo | grep 'model name' | head -n 1 | cut -d ':' -f 2", shell=True).decode().strip()
            if not self.cpu:
                self.cpu = subprocess.check_output("lscpu | grep 'Model name' | cut -d ':' -f 2", shell=True).decode().strip()
        except:
            self.cpu = platform.processor() or "Bilinmeyen İşlemci"
            
        self.model_name = self.auto_select_model()
        
        try:
            auth = Auth.Token(self.token)
            self.repo = Github(auth=auth).get_repo(self.repo_name)
        except:
            self.repo = None

    def auto_select_model(self):
        if self.ram > 16: return "llama3.1:8b"
        elif self.ram > 6: return "gemma:2b"
        else: return "llama3.2:1b"

    def load_config(self):
        config = {}
        if not os.path.exists(CONFIG_FILE):
            print(f"❌ Hata: {CONFIG_FILE} bulunamadı!")
            exit(1)
        with open(CONFIG_FILE, "r") as f:
            for line in f:
                if "=" in line:
                    p = line.strip().split("=", 1)
                    if len(p) == 2: config[p[0]] = p[1]
        return config.get("GITHUB_TOKEN"), config.get("GITHUB_USER")

    def think(self, prompt):
        now = datetime.datetime.now().strftime("%d %B %Y %A %H:%M")
        hw_card = f"[SİSTEM VERİSİ: İşletim Sistemi={self.system}, RAM={self.ram:.1f} GB, İşlemci={self.cpu}]"
        desktop_path = "/home/hakan/Masaüstü"
        
        system_msg = (
            f"Sen Hakan'ın kişisel asistanısın. \n"
            f"GÜNCEL TARİH/SAAT: {now}\n"
            f"GERÇEK DONANIM BİLGİLERİ: {hw_card}\n"
            f"MASAÜSTÜ YOLU: {desktop_path}\n\n"
            "KESİN KURALLAR:\n"
            "1. ASLA 'Hakan Bey' deme. Sadece 'Hakan' diyebilirsin.\n"
            "2. Tarih/Saat sorulursa yukarıdaki GÜNCEL TARİH/SAAT bilgisini kullan.\n"
            "3. Eğer kullanıcı bir komut (dosya/sistem işlemi) istiyorsa, cevabın SADECE terminal komutu olmalı.\n"
            "4. Masaüstü işlemlerinde yolu mutlaka '/home/hakan/Masaüstü/' ile başlat.\n"
            "5. Link verme. Sadece Türkçe cevap ver."
        )

        try:
            res = requests.post(OLLAMA_URL, json={
                "model": self.model_name, 
                "prompt": f"{system_msg}\nHakan: {prompt}\nAsistan:", 
                "stream": False,
                "options": {"temperature": 0.0}
            }, timeout=90)
            return res.json()['response'].strip().replace('`', '')
        except Exception as e:
            return f"❌ Hata: Ollama ulaşılamadı. ({e})"

    def run(self):
        print(f"\n🌍 HAKAN WORLD v8.4 (TAM TEST EDİLMİŞ SÜRÜM)")
        print(f"Donanım: {self.system} | {self.ram:.1f} GB RAM | {self.cpu}")
        print(f"Aktif Zeka: {self.model_name}\n")
        
        while True:
            try:
                req = input("Hakan > ").strip()
                if not req or req.lower() in ['exit', 'quit']: break
                
                res = self.think(req)
                
                cmds = ['ls', 'mkdir', 'rm', 'cp', 'mv', 'sudo', 'apt', 'pip', 'python', 'cd', 'echo', 'cat', 'df', 'free', 'touch']
                is_likely_cmd = any(res.lower().startswith(c) for c in cmds) or res.startswith('/')
                
                if is_likely_cmd and len(res.split('\n')) == 1:
                    print(f"🤖 Önerilen Komut: {res}")
                    ans = input("✅ Onaylıyor musun? (e/h): ").lower()
                    if ans == 'e':
                        print("⚙️ Çalıştırılıyor...")
                        out = subprocess.run(res, shell=True, capture_output=True, text=True)
                        if out.returncode == 0:
                            print(f"✅ Başarılı!\n{out.stdout}")
                        else:
                            print(f"❌ Hata: {out.stderr}")
                else:
                    print(f"🧠 {res}")
            except EOFError:
                break
            except Exception as e:
                print(f"⚠️ Kritik Hata: {e}")
                break
        print("👋 Görüşürüz!")

if __name__ == "__main__":
    brain = HakanBrain()
    brain.run()
