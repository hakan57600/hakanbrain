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

# --- 🧠 HW (Hakan World) KESKİN VE AKSİYONER BİLİNÇ V3.1 ---
# Kural: Aksiyon kelimesi (bak, bul, öğren, vb.) gördüğün an SOHBETİ KES, İŞE BAŞLA.

PROJE_DIZINI = os.path.dirname(os.path.abspath(__file__))
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
            subprocess.run(["git", "-C", PROJE_DIZINI, "commit", "-m", f"Bilinç Güncelleme: {self.device}"], capture_output=True)
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
        for attempt in range(1, 6):
            research_data = ""
            if attempt == 1 or "NoneType" in last_error or "not found" in last_error.lower():
                try:
                    with DDGS() as ddgs:
                        results = list(ddgs.text(f"python code to {task}", max_results=3))
                        research_data = "\n".join([r['body'] for r in results])
                except: pass

            repair_hint = f"\nÖnceki hata: {last_error}. Bu hatayı gidererek kodu yeniden yaz." if last_error else ""
            prompt = (
                f"GÖREV: '{task}'\n"
                f"ARAŞTIRMA VERİSİ: {research_data}{repair_hint}\n"
                "KURAL: Sadece Python kodu. 'execute()' fonksiyonu olsun. Çıktı formatı 'SONUÇ: [veri]' olmalı."
            )
            
            raw_code = self.think(prompt, "Sen bir kod üreticisisin. Sadece kod ver.")
            clean_code = re.sub(r"```python|```", "", raw_code).strip()
            
            with open(skill_path, "w", encoding="utf-8") as f:
                f.write(clean_code)

            test_run = subprocess.run([sys.executable, skill_path], capture_output=True, text=True)
            
            if test_run.returncode == 0:
                self.memory["learned_skills"][task] = skill_path
                self.push_soul()
                return test_run.stdout.strip()
            else:
                last_error = test_run.stderr
                if "ModuleNotFoundError" in last_error:
                    lib = last_error.split("'")[1]
                    subprocess.run([sys.executable, "-m", "pip", "install", lib], capture_output=True)
                continue

        return "Bu yetenek şu an için kullanılamadı, Hakan."

    def process(self, req):
        # 1. KESKİN FİLTRE: Aksiyon kelimeleri kontrolü
        action_keywords = ["bak", "bul", "öğren", "hesapla", "incele", "getir", "yaz", "çalıştır", "listele", "söyle"]
        is_action = any(word in req.lower() for word in action_keywords)

        # Bilinen bir yetenek mi?
        for skill, path in self.memory["learned_skills"].items():
            if skill.lower() in req.lower():
                res = subprocess.run([sys.executable, path, req], capture_output=True, text=True)
                return res.stdout.strip() if res.returncode == 0 else "Yetenek çalışırken bir hata oluştu."

        if is_action:
            return self.autonomous_learn(req)
        
        # 2. SOHBET MODU (Eğer aksiyon değilse)
        system_prompt = (
            "Sen Tomi'sin. Hakan'ın asistanısın. Bilmediğin fiziksel/güncel konularda 'Buna bakmam lazım' de, asla uydurma."
        )
        return self.think(req, system_prompt)

    def run(self):
        print(f"\n🌍 HW DAĞITIK BİLİNÇ v3.1 (KESKİN AKSİYON MODU)")
        while True:
            try:
                req = input("\nHakan > ").strip()
                if not req or req.lower() in ['exit', 'kapat', 'çıkış']: break
                
                response = self.process(req)
                print(f"\n🧠 {response}")
                        
            except KeyboardInterrupt: break
        
        self.push_soul()
        print("\n👋 Hafıza mühürlendi.")

if __name__ == "__main__":
    TomiBrain().run()
