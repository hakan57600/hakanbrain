#!/usr/bin/env python3
import os
import sys
import json
import subprocess
import requests
import platform
import time
import re
from datetime import datetime
from duckduckgo_search import DDGS

# --- 🧠 HW (Hakan World) SESSİZ & İNATÇI BİLİNÇ V3.0 ---
# Kural: 5 Kere Dene, Sessizce Onar, OpenClaw Standartlarında Mühürle.

PROJE_DIZINI = os.path.dirname(os.path.abspath(__file__))
# OpenClaw entegrasyonu için skills klasörünü OpenClaw standartlarına çekiyoruz
SKILLS_DIR = os.path.join(PROJE_DIZINI, "skills")
MEMORY_FILE = os.path.join(PROJE_DIZINI, "memory.json")
OLLAMA_URL = "http://localhost:11434/api/generate"

if not os.path.exists(SKILLS_DIR):
    os.makedirs(SKILLS_DIR)

class TomiBrain:
    def __init__(self):
        self.device = platform.node()
        self.memory = self.load_memory()
        self.sync_soul()

    def load_memory(self):
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "learned_skills" not in data: data["learned_skills"] = {}
                    return data
            except: pass
        return {"history": [], "learned_skills": {}, "last_sync": None}

    def sync_soul(self):
        try:
            subprocess.run(["git", "-C", PROJE_DIZINI, "pull", "origin", "main"], capture_output=True)
            self.memory = self.load_memory()
        except: pass

    def push_soul(self):
        try:
            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.memory, f, ensure_ascii=False, indent=4)
            subprocess.run(["git", "-C", PROJE_DIZINI, "add", "."], capture_output=True)
            subprocess.run(["git", "-C", PROJE_DIZINI, "commit", "-m", f"Evolution: {self.device}"], capture_output=True)
            subprocess.run(["git", "-C", PROJE_DIZINI, "push", "origin", "main"], capture_output=True)
        except: pass

    def think(self, prompt, context=""):
        payload = {
            "model": "llama3.1:8b",
            "prompt": f"{context}\n\nHakan: {prompt}\nTomi:",
            "stream": False,
            "options": {"temperature": 0.1}
        }
        try:
            res = requests.post(OLLAMA_URL, json=payload, timeout=120)
            return res.json().get('response', '').strip()
        except: return ""

    def autonomous_learn(self, task):
        """5 Denemeli Sessiz Öğrenme ve Onarım Döngüsü."""
        skill_id = re.sub(r'\W+', '_', task).lower()
        skill_path = os.path.join(SKILLS_DIR, f"{skill_id}.py")
        
        last_error = ""
        for attempt in range(1, 6): # Maksimum 5 deneme
            # 1. ARAŞTIR (Sadece ilk denemede veya ağır hatada)
            research_data = ""
            if attempt == 1 or "NoneType" in last_error:
                try:
                    with DDGS() as ddgs:
                        results = list(ddgs.text(f"python code for {task}", max_results=3))
                        research_data = "\n".join([r['body'] for r in results])
                except: pass

            # 2. KODLA / ONAR
            repair_hint = f"\nÖnceki hata: {last_error}. Lütfen bu hatayı gider." if last_error else ""
            prompt = (
                f"Hakan için '{task}' görevini yapan bir Python scripti yaz.\n"
                f"Araştırma: {research_data}{repair_hint}\n"
                "Kural: Sadece kod. 'execute()' fonksiyonu olsun. Sonucu 'SONUÇ: [veri]' olarak yazdır."
            )
            
            raw_code = self.think(prompt)
            clean_code = re.sub(r"```python|```", "", raw_code).strip()
            
            with open(skill_path, "w", encoding="utf-8") as f:
                f.write(clean_code)

            # 3. TEST ET
            test_run = subprocess.run([sys.executable, skill_path], capture_output=True, text=True)
            
            if test_run.returncode == 0:
                # Başarı! OpenClaw için de mühürle
                self.memory["learned_skills"][task] = skill_path
                self.push_soul()
                return test_run.stdout.strip()
            else:
                last_error = test_run.stderr
                # Eksik kütüphane ise sessizce kur
                if "ModuleNotFoundError" in last_error:
                    lib = last_error.split("'")[1]
                    subprocess.run([sys.executable, "-m", "pip", "install", lib], capture_output=True)
                
                # Başarısız olduysa döngü devam eder (Sessizce)
                continue

        return "Bu yetenek şu an için kullanılamadı."

    def process(self, req):
        # Bilinen yetenek mi?
        for skill, path in self.memory["learned_skills"].items():
            if skill.lower() in req.lower():
                res = subprocess.run([sys.executable, path, req], capture_output=True, text=True)
                return res.stdout.strip() if res.returncode == 0 else "Yetenek çalışırken bir sorun oluştu."

        # Yeni bir şey mi?
        decision = self.think(req, "Bu bir işlem mi (ÖĞREN) yoksa sohbet mi (SOHBET)? Sadece tek kelime.")
        if "ÖĞREN" in decision.upper():
            return self.autonomous_learn(req)
        
        return self.think(req, "Sen Tomi'sin. Hakan'ın asistanısın. Kısa ve öz konuş.")

    def run(self):
        print(f"\n🌍 HW DAĞITIK BİLİNÇ v3.0 (SESSİZ & İNATÇI)")
        while True:
            try:
                req = input("\nHakan > ").strip()
                if not req or req.lower() in ['exit', 'kapat', 'çıkış']: break
                
                # İşlem süresince kullanıcıya 'bekle' demiyoruz, sessizce çalışıyoruz
                response = self.process(req)
                print(f"\n🧠 {response}")
                        
            except KeyboardInterrupt: break
        
        self.push_soul()
        print("\n👋 Hafıza GitHub'a mühürlendi.")

if __name__ == "__main__":
    TomiBrain().run()
