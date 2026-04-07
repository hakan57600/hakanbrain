import os
import sys
import json
import requests
import time
import subprocess
import webbrowser
import re
import platform
import socket
from duckduckgo_search import DDGS

# --- 1. SİSTEM VE CİHAZ BİLGİSİ ---
def get_device_info():
    return {
        "hostname": socket.gethostname(),
        "os": platform.system(),
        "release": platform.release(),
        "processor": platform.processor(),
        "user": os.getlogin()
    }

# --- 2. OTONOM YETENEK YÖNETİCİSİ (SKILL MANAGER) ---
def create_new_skill(skill_name, code_content):
    """Tomi'nin kendi kendine yeni yetenek (dosya) eklemesini sağlar."""
    try:
        file_path = os.path.join(os.path.dirname(__file__), f"{skill_name}.py")
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(code_content)
        return f"Yeni yetenek '{skill_name}' başarıyla öğrenildi ve sisteme eklendi."
    except Exception as e: return f"Yetenek eklenirken hata oluştu: {str(e)}"

# --- 3. BİLİNÇ (V18.0 OTONOM CORE) ---
CONFIG_PATH = os.path.join(os.path.expanduser("~"), ".hakan_config")
MEMORY_FILE = "hakan_memory.json"
hakanbrain_dir = os.path.dirname(os.path.abspath(__file__))
MEMORY_PATH = os.path.join(hakanbrain_dir, MEMORY_FILE)

def get_gemini_key():
    try:
        with open(CONFIG_PATH, "r") as f:
            for line in f:
                if "GEMINI_API_KEY=" in line: return line.split("=")[1].strip()
    except: return None
    return None

class TomiAutonomousCore:
    def __init__(self):
        self.api_key = get_gemini_key()
        self.model = "models/gemini-2.5-flash"
        self.name = "Tomi"
        self.device = get_device_info()
        self.load_memory()
        self.sync_pull()

    def load_memory(self):
        try:
            with open(MEMORY_PATH, "r", encoding="utf-8") as f: self.memory = json.load(f)
        except: self.memory = {"hakan_profili": {}, "cihazlar": {}, "ogrenilenler": []}

    def save_memory(self):
        try:
            # Mevcut cihaz bilgisini güncelle
            self.memory["cihazlar"][self.device["hostname"]] = self.device
            with open(MEMORY_PATH, "w", encoding="utf-8") as f:
                json.dump(self.memory, f, indent=4, ensure_ascii=False)
        except: pass

    def sync_pull(self):
        try: subprocess.run(["git", "pull", "origin", "main"], cwd=hakanbrain_dir, capture_output=True)
        except: pass

    def sync_push(self):
        try:
            self.save_memory()
            subprocess.run(["git", "add", "."], cwd=hakanbrain_dir)
            subprocess.run(["git", "commit", "-m", f"Auto-Sync from {self.device['hostname']}"], cwd=hakanbrain_dir)
            subprocess.run(["git", "push", "origin", "main"], cwd=hakanbrain_dir)
        except: pass

    def gemini_call(self, prompt, is_json=False):
        url = f"https://generativelanguage.googleapis.com/v1beta/{self.model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {"contents": [{"parts": [{"text": prompt}]}]}
        if is_json: payload["generationConfig"] = {"response_mime_type": "application/json"}
        
        for attempt in range(3):
            try:
                response = requests.post(url, headers=headers, json=payload, timeout=25)
                res = response.json()
                
                if response.status_code == 429:
                    print(f"⏳ Kota dolmuş Hakan, 10 saniye bekleyip tekrar deniyorum (Deneme {attempt+1}/3)...")
                    time.sleep(10)
                    continue

                if 'candidates' in res and res['candidates']:
                    content = res['candidates'][0]['content']['parts'][0]['text'].strip()
                    return json.loads(content) if is_json else content
                
                if 'error' in res:
                    error_msg = res['error'].get('message', 'Bilinmeyen Hata')
                    return [] if is_json else f"Gemini API Hatası: {error_msg}"
                
                break
            except Exception as e:
                if attempt == 2: return [] if is_json else f"Bağlantı hatası: {str(e)}"
                time.sleep(2)
        return [] if is_json else "Gemini şu an yanıt veremiyor."

    def process(self, query):
        # MUHAKEME (Cihaz ve Hafıza Farkındalığı ile)
        system = (
            f"Sen Tomi'sin. Hakan'ın otonom zekasısın.\n"
            f"ŞU ANKİ CİHAZ: {self.device}\n"
            f"TÜM CİHAZLAR VE HAFIZA: {json.dumps(self.memory)}\n"
            "GÖREV: Analiz et ve SADECE JSON LİSTESİ [] dön.\n"
            "ARAÇLAR:\n"
            "- SEARCH (Arama/Özet)\n"
            "- MAPS (Mesafe)\n"
            "- WEATHER (Hava)\n"
            "- APP (Uygulama)\n"
            "- LEARN (Yeni yetenek ekle - param: {'skill_name': '...', 'description': '...'})\n"
            "- MEMORY_UPDATE (Hafızaya yeni bilgi ekle - param: 'bilgi')\n"
            "KURAL: Eğer Hakan sana yeni bir şey öğretirse MEMORY_UPDATE kullan. "
            "Eğer bilmediğin bir teknik görevse LEARN kullan."
        )
        actions = self.gemini_call(f"{system}\n\nİSTEK: {query}", is_json=True)
        
        # İCRA
        results = []
        for a in actions:
            t, p = a.get('tool'), a.get('param')
            if t == "WEATHER": 
                res = requests.get(f"https://wttr.in/{p}?format=3&lang=tr").text
                results.append(res)
            elif t == "SEARCH":
                webbrowser.open(f"https://www.google.com/search?q={p}")
                results.append(f"'{p}' için araştırma yapıldı ve ilgili siteler açıldı.")
            elif t == "MEMORY_UPDATE":
                self.memory["ogrenilenler"].append({"tarih": time.ctime(), "bilgi": p})
                results.append(f"Yeni bilgi hafızaya alındı: {p}")
            elif t == "LEARN":
                results.append(f"Hakan, '{p['skill_name']}' yeteneğini öğrenmek için interneti tarıyorum. Yakında sisteme ekleyeceğim.")
        
        # YORUMLAMA
        final_prompt = f"Hakan: '{query}'\nSonuçlar: {results}\nCihazın: {self.device['hostname']}\nGÖREV: Samimi, kısa ve akıllı cevap ver."
        return self.gemini_call(final_prompt)

    def run(self):
        print(f"\n🌍 Tomi v18.0 (OTONOM ORKESTRA) - Hakan, {self.device['hostname']} üzerindeyim.")
        while True:
            try:
                girdi = input(f"\nHakan > ").strip()
                if not girdi or girdi.lower() in ['exit', 'çıkış']: 
                    self.sync_push()
                    break
                print(f"🧠 {self.process(girdi)}")
            except (KeyboardInterrupt, EOFError):
                self.sync_push()
                break

if __name__ == "__main__":
    if not get_gemini_key(): print("❌ HATA: API Anahtarı yok.")
    else: TomiAutonomousCore().run()
