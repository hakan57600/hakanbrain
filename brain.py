#!/usr/bin/env python3
import os
import sys
import json
import subprocess
import requests
import platform
import time
from datetime import datetime

# --- 🧠 HW (Hakan World) DAĞITIK BİLİNÇ V1.0 ---
# Ruh (GitHub) + Beden (Herhangi bir Cihaz) + Yerel Hafıza (Offline)

PROJE_DIZINI = os.path.dirname(os.path.abspath(__file__))
MEMORY_FILE = os.path.join(PROJE_DIZINI, "memory.json")
OLLAMA_URL = "http://localhost:11434/api/generate"

class HakanBrain:
    def __init__(self):
        self.system = platform.system()
        self.device_name = platform.node()
        self.memory = self.load_local_memory()
        self.sync_with_soul() # GitHub'dan ruhu (geçmişi) çek

    def load_local_memory(self):
        """Offline mod için yerel hafızayı yükler."""
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: pass
        return {"history": [], "hakan_profile": {}, "last_sync": None}

    def sync_with_soul(self):
        """GitHub'dan en son hafızayı ve ruhu çeker (git pull)."""
        print(f"🔄 Ruh (GitHub) senkronize ediliyor... [{self.device_name}]")
        try:
            # Git pull işlemini sessizce yap
            subprocess.run(["git", "-C", PROJE_DIZINI, "pull", "origin", "main"], 
                           capture_output=True, text=True)
            # Pull sonrası yerel hafızayı güncelle
            self.memory = self.load_local_memory()
            print("✅ Ruh uyanık ve güncel, Hakan.")
        except:
            print("⚠️ Ruh senkronizasyonu başarısız (Offline mod aktif).")

    def seal_soul(self):
        """Hafızayı mühürler ve GitHub'a gönderir (git push)."""
        print("\n💾 Hafıza mühürleniyor...")
        try:
            self.memory["last_sync"] = datetime.now().isoformat()
            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.memory, f, ensure_ascii=False, indent=4)
            
            # Git push işlemleri
            subprocess.run(["git", "-C", PROJE_DIZINI, "add", "."], capture_output=True)
            subprocess.run(["git", "-C", PROJE_DIZINI, "commit", "-m", f"Brain Sync: {self.device_name} - {datetime.now()}"], capture_output=True)
            subprocess.run(["git", "-C", PROJE_DIZINI, "push", "origin", "main"], capture_output=True)
            print("✅ Hafıza GitHub'a mühürlendi. Her cihazda hatırlayacağım.")
        except Exception as e:
            print(f"⚠️ Mühürleme hatası (Yerel yedek alındı): {e}")

    def think(self, prompt):
        """Cihazın kendi işlemcisinde (Ollama) düşünür."""
        # Cihazın durumuna göre sistem mesajı (Kotayı burada eziyoruz)
        system_msg = (
            f"Sen Tomi'sin. Hakan'ın kotasız ve unutmayan asistanısın. Cihaz: {self.device_name}.\\n"
            "KURAL 1: Sadece 'Hakan' de.\\n"
            "KURAL 2: Hafızandaki geçmişe göre cevap ver. Uydurma.\\n"
            "KURAL 3: Terminal komutu istense sadece komutu yaz."
        )

        payload = {
            "model": "llama3.1:8b", # Cihaza göre dinamikleşecek
            "prompt": f"{system_msg}\nGeçmiş: {self.memory['history'][-5:]}\nHakan: {prompt}\nTomi:",
            "stream": False
        }

        try:
            res = requests.post(OLLAMA_URL, json=payload, timeout=90)
            return res.json().get('response', 'Hata: Boş yanıt.').strip()
        except:
            return "❌ Yerel zeka (Ollama) yanıt vermiyor. (ollama serve açık mı?)"

    def process(self, req):
        if not req: return
        res = self.think(req)
        
        # Hafızaya ekle
        self.memory["history"].append({"q": req, "a": res, "t": datetime.now().isoformat()})
        if len(self.memory["history"]) > 100: self.memory["history"] = self.memory["history"][-100:]
        
        return res

    def run(self):
        print(f"\n🌟 HW DAĞITIK TOMI AKTİF | Cihaz: {self.device_name}")
        print("Çıkış için 'exit' veya 'kapat' yazabilirsin.\n")
        
        while True:
            try:
                req = input("Hakan > ").strip()
                if not req: continue
                if req.lower() in ['exit', 'quit', 'kapat', 'çıkış']:
                    self.seal_soul() # Kapatırken mühürle
                    break
                
                start_time = time.time()
                res = self.process(req)
                print(f"\n🧠 {res} ({int(time.time() - start_time)}sn)\n")
                
            except KeyboardInterrupt:
                self.seal_soul()
                break
        print("👋 Görüşürüz Hakan.")

if __name__ == "__main__":
    brain = HakanBrain()
    brain.run()
