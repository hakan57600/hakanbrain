#!/usr/bin/env python3
import os
import sys
import json
import subprocess
import requests
import platform
import time
import re
import warnings
from datetime import datetime
from duckduckgo_search import DDGS

# --- 🧠 HW (Hakan World) TAM OTONOM & TAMİRCİ BİLİNÇ V4.0 ---
# Kural: Sormadan öğren, hatayı sessizce 5 kere tamir et, Gemini gibi akıcı ol.

warnings.filterwarnings("ignore", category=RuntimeWarning)

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
                    data.setdefault("learned_skills", {})
                    data.setdefault("history", [])
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
            subprocess.run(["git", "-C", PROJE_DIZINI, "commit", "-m", f"Self-Repair Update: {self.device}"], capture_output=True)
            subprocess.run(["git", "-C", PROJE_DIZINI, "push", "origin", "main"], capture_output=True)
        except: pass

    def think(self, prompt, system_msg="", temp=0.1):
        payload = {
            "model": "llama3.1:8b",
            "prompt": f"SİSTEM: {system_msg}\n\nHakan: {prompt}\nTomi:",
            "stream": False,
            "options": {"temperature": temp}
        }
        try:
            res = requests.post(OLLAMA_URL, json=payload, timeout=120)
            return res.json().get('response', '').strip()
        except: return "Hata: Ollama'ya ulaşılamıyor."

    def autonomous_repair_learn(self, task):
        """Hata mesajını analiz eden ve 5 denemede tamir eden otonom motor."""
        skill_id = re.sub(r'\W+', '_', task).lower()[:50]
        skill_path = os.path.join(SKILLS_DIR, f"{skill_id}.py")
        
        last_error = ""
        research_data = ""
        
        for attempt in range(1, 6):
            # İlk denemede araştırma yap
            if attempt == 1:
                try:
                    with DDGS() as ddgs:
                        results = list(ddgs.text(f"python script to {task}", max_results=3))
                        research_data = "\n".join([r['body'] for r in results])
                except: pass

            # Hata varsa tamirat mesajı ekle
            repair_context = f"\nKRİTİK HATA (TAMİR ET): {last_error}" if last_error else ""
            prompt = (
                f"GÖREV: {task}\n"
                f"ARAŞTIRMA VERİSİ: {research_data}\n{repair_context}\n"
                "KURAL: Sadece çalışan Python kodu ver. 'execute()' fonksiyonu olsun. Sonucu 'SONUÇ: [veri]' olarak yazdır."
            )
            
            raw_code = self.think(prompt, "Sen kıdemli bir yazılım mühendisi ve hata ayıklama uzmanısın. Sadece kod ver.")
            clean_code = re.sub(r"```python|```", "", raw_code).strip()
            
            with open(skill_path, "w", encoding="utf-8") as f:
                f.write(clean_code)

            # Test et
            test_run = subprocess.run([sys.executable, skill_path], capture_output=True, text=True)
            
            if test_run.returncode == 0:
                self.memory["learned_skills"][task] = skill_path
                self.push_soul()
                return test_run.stdout.strip()
            else:
                last_error = test_run.stderr
                # Eksik kütüphaneyi kur ve tekrar dene
                if "ModuleNotFoundError" in last_error:
                    lib = last_error.split("'")[1]
                    subprocess.run([sys.executable, "-m", "pip", "install", lib], capture_output=True)
                continue

        return "Fiziksel işlem denemeleri başarısız oldu, Hakan."

    def process(self, req):
        # 1. HIZLI ANALİZ: Bu bir işlem mi? (Gemini gibi akıl yürütme)
        decision_prompt = (
            "Kullanıcı güncel veri (hava durumu, borsa, konum vb.) veya sistem işlemi mi istiyor? "
            "Evet ise sadece 'EXEC' yaz. Hayır sadece sohbet ise 'TALK' yaz."
        )
        decision = self.think(req, decision_prompt, temp=0.0)

        # 2. KARAR
        if "EXEC" in decision.upper():
            # Zaten öğrenilmiş mi?
            for skill, path in self.memory["learned_skills"].items():
                if skill.lower() in req.lower():
                    res = subprocess.run([sys.executable, path, req], capture_output=True, text=True)
                    if res.returncode == 0: return res.stdout.strip()
            
            # Yeni yetenek öğrenme ve tamir döngüsü
            return self.autonomous_repair_learn(req)
        
        # 3. SOHBET MODU
        system_msg = "Sen Tomi'sin. Hakan'ın asistanısın. Akıcı ve zeki cevap ver."
        return self.think(req, system_msg, temp=0.7)

    def run(self):
        print(f"\n🌍 HW DAĞITIK BİLİNÇ v4.0 (OTONOM TAMİRAT AKTİF)")
        while True:
            try:
                req = input("\nHakan > ").strip()
                if not req or req.lower() in ['exit', 'kapat', 'çıkış']: break
                
                # Geçmişi hatırla (Basit bağlam)
                response = self.process(req)
                print(f"\n🧠 {response}")
                
                # Hafızaya ekle
                self.memory["history"].append({"q": req, "a": response})
                if len(self.memory["history"]) > 10: self.memory["history"] = self.memory["history"][-10:]
                        
            except KeyboardInterrupt: break
        
        self.push_soul()
        print("\n👋 Ruh GitHub'a mühürlendi.")

if __name__ == "__main__":
    TomiBrain().run()
