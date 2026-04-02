import os
import json
import platform
import subprocess
import requests
import sys
import time
import re
from github import Github, Auth

# --- AYARLAR ---
CONFIG_FILE = os.path.expanduser("~/Masaüstü/.hakan_config")
MEMORY_FILE = os.path.expanduser("~/Masaüstü/memory.json")
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2:1b"

class HybridMemory:
    def __init__(self, token, repo_name):
        auth = Auth.Token(token)
        self.gh = Github(auth=auth)
        try:
            self.repo = self.gh.get_repo(repo_name)
        except Exception as e:
            print(f"❌ Repo erişim hatası: {e}")
            exit()
        self.local_data = self.load_local()

    def load_local(self):
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"history": [], "learned_commands": {}, "last_sync": None}

    def sync(self):
        print("🔄 GitHub ile senkronize ediliyor...")
        try:
            content_str = json.dumps(self.local_data, indent=4)
            try:
                contents = self.repo.get_contents("memory.json")
                self.repo.update_file("memory.json", "Brain Sync: Update", content_str, contents.sha)
            except:
                self.repo.create_file("memory.json", "Brain Sync: Initial", content_str)
            print("✅ Senkronizasyon Tamamlandı!")
        except Exception as e:
            print(f"⚠️ Senkronizasyon Hatası: {e}")

class HakanBrain:
    def __init__(self):
        self.token, self.user = self.load_config()
        self.repo_name = f"{self.user}/hakanbrain"
        self.memory = HybridMemory(self.token, self.repo_name)
        self.system = platform.system()

    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            print(f"❌ {CONFIG_FILE} bulunamadı!")
            exit()
        config = {}
        with open(CONFIG_FILE, "r") as f:
            for line in f:
                if "=" in line:
                    parts = line.strip().split("=", 1)
                    if len(parts) == 2: config[parts[0]] = parts[1]
        return config.get("GITHUB_TOKEN"), config.get("GITHUB_USER")

    def clean_command(self, raw_response):
        """Yapay zekadan gelen cevabı sadece geçerli bir komuta dönüştürür"""
        # İlk satırı al (açıklamaları at)
        first_line = raw_response.strip().split('\n')[0]
        # Backtickleri temizle
        cmd = first_line.replace('`', '').replace('Command:', '').strip()
        # Eğer hala metin kalmışsa (bazı modeller 'Burada bir komut var:' diyebilir)
        # Sadece bilinen bash komutlarıyla başlayan kısmı yakalamaya çalış
        return cmd

    def think(self, prompt):
        print(f"🧠 {MODEL_NAME} ile düşünülüyor...")
        system_msg = f"Sen bir Linux/Terminal asistanısın. Görevin: Kullanıcının isteğini sadece TEK BİR terminal komutu olarak yazmaktır. Kesinlikle açıklama yapma, cümle kurma. Sadece komut."
        
        try:
            payload = {
                "model": MODEL_NAME, 
                "prompt": f"{system_msg}\nİstek: {prompt}\nKomut:", 
                "stream": False,
                "options": {"num_thread": 4, "temperature": 0.0} # 0.0 temperature ile tutarlı komut üretimi
            }
            res = requests.post(OLLAMA_URL, json=payload, timeout=30)
            raw_response = res.json()['response']
            return self.clean_command(raw_response)
        except Exception as e:
            return f"echo '❌ Ollama Hatası: {str(e)}'"

    def execute_and_sync(self, req, cmd):
        print(f"🤖 Önerilen Komut: {cmd}")
        if "❌" in cmd:
            print(cmd)
            return

        # Otomatik deneme/test modunda mıyız kontrol et (input stdin'den geliyorsa onay bekleme)
        if not sys.stdin.isatty():
            ans = 'e'
            print("🤖 Test Modu: Otomatik onaylandı.")
        else:
            ans = input("✅ Onaylıyor musun? (e/h): ").lower()

        if ans == 'e':
            print("⚙️ Çalıştırılıyor...")
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ BAŞARILI!\n--- ÇIKTI ---\n{result.stdout}")
                self.memory.local_data["history"].append({"request": req, "command": cmd, "status": "success", "time": time.ctime()})
            else:
                print(f"❌ HATA!\n--- HATA ---\n{result.stderr}")
                self.memory.local_data["history"].append({"request": req, "command": cmd, "status": "error", "time": time.ctime()})
            
            self.memory.sync()
        else:
            print("⚠️ İşlem iptal edildi.")

    def run(self):
        print(f"\n🚀 HAKAN BRAIN v3.4 [HIZLI VE KARARLI MOD]")
        while True:
            try:
                req = input("\nHakan > ").strip()
                if not req or req.lower() in ['exit', 'quit']: break
                cmd = self.think(req)
                self.execute_and_sync(req, cmd)
            except KeyboardInterrupt: break
            except EOFError: break # Pipe ile biterse döngüden çık
        print("👋 Görüşürüz!")

if __name__ == "__main__":
    brain = HakanBrain()
    brain.run()
