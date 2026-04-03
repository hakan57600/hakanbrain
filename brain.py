import os
import json
import platform
import subprocess
import requests
import sys
import psutil
import time
import datetime
import re
from github import Github, Auth

# --- AYARLAR ---
CONFIG_FILE = os.path.expanduser("~/.hakan_config")
MEMORY_FILE = os.path.expanduser("~/hakan_memory.json")
OLLAMA_URL = "http://localhost:11434/api/generate"

class HakanBrain:
    def __init__(self):
        self.token, self.user = self.load_config()
        self.memory = self.load_memory()
        self.system = platform.system()
        self.ram = psutil.virtual_memory().total / (1024**3)
        self.cpu = self.get_cpu_info()
        self.model_name = self.auto_select_model()
        self.assistant_name = "Tomi"
        self.user_name = "Hakan"

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
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"learned_facts": [], "conversation_history": [], "style": "Samimi ve teknik"}

    def save_memory(self):
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=4)

    def think(self, prompt):
        now = datetime.datetime.now().strftime("%d %B %Y %A %H:%M")
        hw_card = f"[SİSTEM: {self.system}, RAM: {self.ram:.1f}GB, CPU: {self.cpu}]"
        mem_context = "\n".join(self.memory["learned_facts"][-10:]) # Son 10 bilgiyi hatırla
        
        system_msg = (
            f"Senin adın {self.assistant_name}. Kullanıcının adı {self.user_name}.\n"
            f"GÜNCEL ZAMAN: {now}\n"
            f"DONANIM: {hw_card}\n"
            f"BİLİNEN GERÇEKLER:\n{mem_context}\n\n"
            "KURALLAR:\n"
            "1. Sadece 'Hakan' diye hitap et.\n"
            "2. Matematiksel işlemleri doğrudan çöz.\n"
            "3. Dosya/Sistem işlemi gerekiyorsa SADECE terminal komutu ver.\n"
            "4. Bilmediğin bir bilgi olursa 'SEARCH: <sorgu>' formatında cevap ver ki araştırayım.\n"
            "5. Yeni bir bilgi öğrendiğinde 'LEARN: <bilgi>' formatında belirt.\n"
            "6. Cevaplar Türkçe ve akıcı olsun."
        )

        try:
            res = requests.post(OLLAMA_URL, json={
                "model": self.model_name, 
                "prompt": f"{system_msg}\nHakan: {prompt}\n{self.assistant_name}:", 
                "stream": False,
                "options": {"temperature": 0.1}
            }, timeout=90).json()
            response = res['response'].strip().replace('`', '')
            
            # Öğrenme mekanizması
            if "LEARN:" in response:
                fact = response.split("LEARN:")[1].split("\n")[0].strip()
                if fact not in self.memory["learned_facts"]:
                    self.memory["learned_facts"].append(fact)
                    self.save_memory()
            
            return response
        except Exception as e:
            return f"❌ Hata: {e}"

    def run_command(self, cmd):
        print(f"⚙️ Çalıştırılıyor: {cmd}")
        try:
            out = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
            if out.returncode == 0:
                print(f"✅ Başarılı!\n{out.stdout}")
                return out.stdout
            else:
                print(f"❌ Hata: {out.stderr}")
                return out.stderr
        except Exception as e:
            print(f"⚠️ Hata: {e}")
            return str(e)

    def run(self):
        print(f"\n🌍 {self.assistant_name.upper()} WORLD v8.5")
        print(f"Merhaba {self.user_name}! Sistem hazır. (Model: {self.model_name})")
        
        while True:
            try:
                req = input(f"{self.user_name} > ").strip()
                if not req or req.lower() in ['exit', 'quit']: break
                
                if req.lower() == "test":
                    self.self_test()
                    continue

                res = self.think(req)
                
                if "SEARCH:" in res:
                    query = res.split("SEARCH:")[1].strip()
                    print(f"🔍 Araştırıyorum: {query}...")
                    # Burada basit bir ddgr veya curl araması simüle edilebilir
                    search_res = self.run_command(f"curl -s 'https://api.duckduckgo.com/?q={query}&format=json' | jq .Abstract")
                    print(f"💡 Bilgi Edinildi: {search_res}")
                    res = self.think(f"Arama sonucu şudur: {search_res}. Şimdi sorumu cevapla: {req}")

                cmds = ['ls', 'mkdir', 'rm', 'cp', 'mv', 'sudo', 'apt', 'pip', 'python', 'cd', 'echo', 'cat', 'df', 'free', 'touch', 'git']
                is_cmd = any(res.lower().startswith(c) for c in cmds) or res.startswith('/')
                
                if is_cmd and len(res.split('\n')) == 1:
                    print(f"🤖 Komut Algılandı: {res}")
                    if input("✅ Onaylıyor musun? (e/h): ").lower() == 'e':
                        self.run_command(res)
                else:
                    print(f"🧠 {res}")

            except EOFError: break
            except Exception as e:
                print(f"⚠️ Hata: {e}")
        print("👋 Görüşürüz!")

    def self_test(self):
        print("\n🧪 --- KENDİ KENDİNİ TEST MODU BAŞLATILDI ---")
        tests = [
            ("Adın ne?", "Tomi"),
            ("Ben kimim?", "Hakan"),
            ("25 * 4 kaç eder?", "100"),
            ("Masaüstünde 'test_dosyası.txt' oluştur.", "touch"),
            ("Sinop Gerze hangi ülkededir? (Araştır ve Öğren)", "LEARN")
        ]
        
        for q, expected in tests:
            print(f"\n❓ Test Sorusu: {q}")
            res = self.think(q)
            print(f"Answer: {res}")
            if expected.lower() in res.lower():
                print("✅ TEST BAŞARILI")
            else:
                print(f"❌ TEST BAŞARISIZ (Beklenen: {expected})")
        print("\n🧪 --- TEST TAMAMLANDI ---\n")

if __name__ == "__main__":
    brain = HakanBrain()
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        brain.self_test()
    else:
        brain.run()
