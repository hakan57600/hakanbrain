import os
import sys
import json
import requests
import time
import subprocess

# Düz Yapı İçe Aktarmaları
hakanbrain_dir = os.path.dirname(os.path.abspath(__file__))
if hakanbrain_dir not in sys.path:
    sys.path.insert(0, hakanbrain_dir)

from unified_tools import tool_uygulama_kesfet_ve_ac, tool_internet_ara_ve_ac, tool_hava_durumu, tool_mesafe_hesapla

CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".hakan_config")
MEMORY_FILE = "hakan_memory.json"
MEMORY_PATH = os.path.join(hakanbrain_dir, MEMORY_FILE)

def get_gemini_key():
    try:
        with open(CONFIG_PATH, "r") as f:
            for line in f:
                if "GEMINI_API_KEY=" in line: return line.split("=")[1].strip()
    except: return None
    return None

class TomiUniversalCore:
    def __init__(self):
        self.api_key = get_gemini_key()
        self.model = "models/gemini-2.5-flash"
        self.name = "Tomi"
        self.sync_pull() # Açılışta buluttan çek
        self.load_memory()

    def sync_pull(self):
        try:
            subprocess.run(["git", "pull", "origin", "master"], cwd=hakanbrain_dir, capture_output=True)
        except: pass

    def sync_push(self):
        try:
            subprocess.run(["git", "add", MEMORY_FILE], cwd=hakanbrain_dir)
            subprocess.run(["git", "commit", "-m", "Memory Auto-Sync"], cwd=hakanbrain_dir)
            subprocess.run(["git", "push", "origin", "master"], cwd=hakanbrain_dir)
        except: pass

    def load_memory(self):
        try:
            with open(MEMORY_PATH, "r", encoding="utf-8") as f: self.memory = json.load(f)
        except: self.memory = {}

    def get_hakan_context(self):
        profile = self.memory.get("hakan_profili", {})
        if not profile: return "Hakan hakkında özel bilgi yok."
        return "\n".join([f"- {k}: {', '.join(v) if isinstance(v, list) else v}" for k, v in profile.items()])

    def gemini_call(self, prompt, is_json=False):
        url = f"https://generativelanguage.googleapis.com/v1beta/{self.model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        if is_json: payload["generationConfig"] = {"response_mime_type": "application/json"}
        
        try:
            res = requests.post(url, headers=headers, json=payload, timeout=20).json()
            if 'candidates' in res:
                content = res['candidates'][0]['content']['parts'][0]['text'].strip()
                return json.loads(content) if is_json else content
            return [] if is_json else "Gemini şu an yanıt veremiyor."
        except: return [] if is_json else "Bağlantı hatası."

    def process(self, query):
        # Muhakeme
        system = f"Sen Tomi'sin. Hakan'ın asistanısın. Hafıza:\n{self.get_hakan_context()}\nGÖREV: Analiz et ve SADECE JSON [] dön.\nARAÇLAR: SEARCH, WEATHER, MAPS, APP.\nKURAL: Kişisel sorularda [] dön."
        actions = self.gemini_call(f"{system}\n\nİSTEK: {query}", is_json=True)
        
        # İcra
        data = []
        for a in actions:
            t, p = a.get('tool'), a.get('param')
            if t == "WEATHER": data.append(tool_hava_durumu(p))
            elif t == "MAPS": data.append(tool_mesafe_hesapla(p))
            elif t == "SEARCH": data.append(tool_internet_ara_ve_ac(p))
            elif t == "APP": data.append(tool_uygulama_kesfet_ve_ac(p))
        
        # Yorum
        final_prompt = f"Soru: '{query}'\nVeriler: {data}\nHafıza: {self.get_hakan_context()}\nGÖREV: Kısa, öz ve samimi cevap ver. Gereksiz yorum yapma. 'Bey' deme."
        response = self.gemini_call(final_prompt)
        
        # Hafıza Güncelleme ve Senkronizasyon (Eğer yeni bir şey öğrenildiyse buraya kod eklenebilir)
        return response

    def run(self):
        print(f"\n🌍 Tomi v17.0 (EVRENSEL BEYİN) - Hakan, her cihazda emrindeyim.")
        while True:
            try:
                girdi = input(f"\nHakan > ").strip()
                if not girdi or girdi.lower() in ['exit', 'çıkış']: 
                    self.sync_push() # Kapanırken buluta mühürle
                    break
                print(f"🧠 {self.process(girdi)}")
            except (KeyboardInterrupt, EOFError):
                self.sync_push()
                break

if __name__ == "__main__":
    if not get_gemini_key(): print("❌ HATA: API Anahtarı bulunamadı.")
    else: TomiUniversalCore().run()
