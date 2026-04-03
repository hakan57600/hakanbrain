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
MEMORY_FILE = os.path.expanduser("~/hakan_memory.json")
OLLAMA_URL = "http://localhost:11434/api/generate"

class HakanBrain:
    def __init__(self):
        self.assistant_name = "Tomi"
        self.user_name = "Hakan"
        self.system = platform.system()
        self.ram = psutil.virtual_memory().total / (1024**3)
        self.cpu = self.get_cpu_info()
        self.token, self.user = self.load_config()
        self.memory = self.load_memory()
        self.model_name = self.auto_select_model()

    def get_cpu_info(self):
        try:
            if self.system == "Linux":
                return subprocess.check_output("cat /proc/cpuinfo | grep 'model name' | head -n 1 | cut -d ':' -f 2", shell=True).decode().strip()
            return platform.processor()
        except: return "Bilinmeyen İşlemci"

    def auto_select_model(self):
        if self.ram > 16: return "llama3.1:8b"
        elif self.ram > 6: return "gemma:2b"
        return "llama3.2:1b"

    def load_config(self):
        config = {}
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r") as f:
                for line in f:
                    if "=" in line:
                        p = line.strip().split("=", 1)
                        config[p[0]] = p[1]
        return config.get("GITHUB_TOKEN"), config.get("GITHUB_USER", "hakan57600")

    def load_memory(self):
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: pass
        return {"learned_facts": [], "user_prefs": {}}

    def save_memory(self):
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=4)

    def think(self, prompt, context=""):
        now = datetime.datetime.now().strftime("%d %B %Y %A %H:%M")
        hw = f"[SİSTEM: {self.system}, RAM: {self.ram:.1f}GB, CPU: {self.cpu}]"
        mem = "\n".join(self.memory["learned_facts"][-10:])
        
        system_msg = (
            f"Senin adın {self.assistant_name}. Kullanıcının adı {self.user_name}.\n"
            f"ZAMAN: {now} | DONANIM: {hw}\n"
            f"BİLİNENLER:\n{mem}\n"
            f"EK BİLGİ: {context}\n\n"
            "KURALLAR:\n"
            "1. Sadece 'Hakan' de.\n"
            "2. Matematik: Doğrudan sonuç ver.\n"
            "3. Dosya/Sistem: SADECE terminal komutu (tek satır).\n"
            "4. Bilmediğin bir şey için: 'SEARCH: <sorgu>'.\n"
            "5. Öğrendiğin yeni bilgiyi: 'LEARN: <bilgi>'.\n"
            "6. Tamamen Türkçe konuş."
        )

        try:
            res = requests.post(OLLAMA_URL, json={
                "model": self.model_name, 
                "prompt": f"{system_msg}\nHakan: {prompt}\n{self.assistant_name}:", 
                "stream": False,
                "options": {"temperature": 0.0}
            }, timeout=90).json()
            return res['response'].strip().replace('`', '')
        except Exception as e:
            return f"❌ Hata: {e}"

    def run_command(self, cmd):
        try:
            out = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=15)
            return out.stdout if out.returncode == 0 else out.stderr
        except Exception as e:
            return str(e)

    def web_search(self, query):
        # Basit bir arama simülasyonu (Gerçek arama için ddgr veya curl kullanılabilir)
        # Şimdilik DuckDuckGo API simülasyonu yapıyoruz
        try:
            res = requests.get(f"https://api.duckduckgo.com/?q={query}&format=json", timeout=10).json()
            return res.get("AbstractText", "Bilgi bulunamadı.")
        except:
            return "İnternet araması başarısız."

    def process(self, req):
        # Ana döngü mantığı: Düşün -> (Gerekirse Ara -> Tekrar Düşün) -> Cevapla -> (Gerekirse Öğren)
        res = self.think(req)
        
        # 1. ARAMA GEREKİYOR MU?
        if "SEARCH:" in res:
            query = res.split("SEARCH:")[1].split("\n")[0].strip()
            print(f"🔍 Araştırıyorum: {query}...")
            search_result = self.web_search(query)
            res = self.think(req, context=f"Arama Sonucu: {search_result}")

        # 2. ÖĞRENME VAR MI?
        if "LEARN:" in res:
            fact = res.split("LEARN:")[1].split("\n")[0].strip()
            if fact not in self.memory["learned_facts"]:
                self.memory["learned_facts"].append(fact)
                self.save_memory()
                print(f"🧠 Yeni Bilgi Hafızaya Alındı: {fact}")

        # 3. KOMUT VAR MI?
        cmds = ['ls', 'mkdir', 'rm', 'cp', 'mv', 'sudo', 'apt', 'pip', 'python', 'cd', 'echo', 'cat', 'df', 'free', 'touch', 'git']
        is_cmd = any(res.lower().startswith(c) for c in cmds) or res.startswith('/')
        
        if is_cmd and len(res.split('\n')) == 1:
            print(f"🤖 Komut Algılandı: {res}")
            if input("✅ Onaylıyor musun? (e/h): ").lower() == 'e':
                out = self.run_command(res)
                print(f"💻 Çıktı:\n{out}")
            return None
        
        return res

    def self_test(self):
        print("\n🧪 --- TAM SİSTEM TESTİ BAŞLADI ---")
        test_cases = [
            ("Adın ne?", "Tomi"),
            ("Ben kimim?", "Hakan"),
            ("125 + 125 kaç eder?", "250"),
            ("Masaüstünde 'tomi_test.txt' adında bir dosya oluştur.", "touch"),
            ("Türkiye'nin başkenti neresidir? (Öğren ve kaydet)", "Ankara")
        ]
        
        success_count = 0
        for q, expected in test_cases:
            print(f"\n❓ Soru: {q}")
            res = self.process(q)
            if res is None: # Komut çalıştırıldı demektir
                print("✅ Komut Testi Tamam.")
                success_count += 1
                continue
                
            print(f"🧠 Cevap: {res}")
            if expected.lower() in res.lower():
                print("✅ Başarılı")
                success_count += 1
            else:
                print(f"❌ Başarısız (Beklenen içerik: {expected})")
        
        print(f"\n📊 Sonuç: {success_count}/{len(test_cases)} başarılı.")
        return success_count == len(test_cases)

    def run(self):
        print(f"\n🌍 {self.assistant_name.upper()} WORLD v9.0")
        while True:
            try:
                req = input(f"{self.user_name} > ").strip()
                if not req or req.lower() in ['exit', 'quit']: break
                if req.lower() == "test":
                    self.self_test()
                    continue
                
                res = self.process(req)
                if res: print(f"🧠 {res}")
            except EOFError: break
            except Exception as e: print(f"⚠️ Hata: {e}")
        print("👋 Görüşürüz!")

if __name__ == "__main__":
    brain = HakanBrain()
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        if brain.self_test(): sys.exit(0)
        else: sys.exit(1)
    else:
        brain.run()
