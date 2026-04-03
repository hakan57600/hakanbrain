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

def tr_lower(text):
    # Türkçe I-İ dönüşümü için özel lower
    return text.replace('İ', 'i').replace('I', 'ı').lower()

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
        return {"learned_facts": []}

    def save_memory(self):
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.memory, f, ensure_ascii=False, indent=4)

    def think(self, prompt, context=""):
        now = datetime.datetime.now().strftime("%d %B %Y %A %H:%M")
        hw = f"[SİSTEM: {self.system}, RAM: {self.ram:.1f}GB, CPU: {self.cpu}]"
        mem_list = "\n".join([f"- {f}" for f in self.memory["learned_facts"]])
        
        system_msg = (
            f"Senin adın {self.assistant_name}. Kullanıcının adı {self.user_name}.\n"
            f"ZAMAN: {now} | DONANIM: {hw}\n"
            f"HAFIZA:\n{mem_list}\n"
            f"EK: {context}\n\n"
            "KURALLAR:\n"
            "1. Sadece 'Hakan' de.\n"
            "2. Yeni Bilgi: 'LEARN: <bilgi>'.\n"
            "3. Sadece Türkçe."
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

    def process(self, req):
        # KESİN TEMİZLİK (Türkçe Duyarlı)
        req_clean = tr_lower(req)
        if "unut" in req_clean or "sil" in req_clean:
            # Kelimeleri ayır ve 3 harften büyük olanları hafızada ara
            words = re.findall(r'\w+', req_clean)
            for w in words:
                if w not in ["unut", "sil", "bunu", "adını"] and len(w) > 3:
                    original_len = len(self.memory["learned_facts"])
                    self.memory["learned_facts"] = [f for f in self.memory["learned_facts"] if tr_lower(w) not in tr_lower(f)]
                    if len(self.memory["learned_facts"]) < original_len:
                        print(f"🗑️ '{w}' ile ilgili bilgi hafızadan silindi.")
            self.save_memory()

        res = self.think(req)
        
        if "LEARN:" in res:
            fact = res.split("LEARN:")[1].strip()
            if fact not in self.memory["learned_facts"]:
                self.memory["learned_facts"].append(fact)
                self.save_memory()
                print(f"🧠 Öğrenildi: {fact}")

        return res

    def self_test(self):
        print("\n🧪 --- v14.0 TÜRKÇE HAFIZA TESTİ ---")
        self.memory["learned_facts"] = ["İstanbul en büyük şehirdir."]
        self.save_memory()
        
        print("\n❓ Soru: İstanbul'u unut, Ankara'yı öğren.")
        self.process("İstanbul'u unut, Ankara'yı öğren.")
        
        print(f"❓ Güncel Hafıza: {self.memory['learned_facts']}")
        
        if any("Ankara" in f for f in self.memory["learned_facts"]) and not any("İstanbul" in f for f in self.memory["learned_facts"]):
            print("✅ TEST BAŞARILI.")
            return True
        else:
            print("❌ TEST BAŞARISIZ.")
            return False

if __name__ == "__main__":
    brain = HakanBrain()
    if len(sys.argv) > 1 and sys.argv[1] == "--test":
        if brain.self_test(): sys.exit(0)
        else: sys.exit(1)
    else:
        brain.run()
