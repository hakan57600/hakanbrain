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

# --- 🧠 HW (Hakan World) BAĞLAM TAKİPLİ & OTOMATİK TAMİRATLI BİLİNÇ V3.2 ---
# Kural: Hafızayı asla koparma, hatayı sessizce tamir et, 5 kere sonuna kadar zorla.

warnings.filterwarnings("ignore", category=RuntimeWarning) # DDGS uyarılarını sustur

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
                    if "history" not in data: data["history"] = []
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
            subprocess.run(["git", "-C", PROJE_DIZINI, "commit", "-m", f"Tamirat ve Bağlam: {self.device}"], capture_output=True)
            subprocess.run(["git", "-C", PROJE_DIZINI, "push", "origin", "main"], capture_output=True)
        except: pass

    def think(self, prompt, context_msgs=[]):
        # Geçmiş diyalogları bağlam olarak ekle
        history_str = "\n".join([f"Hakan: {h['q']}\nTomi: {h['a']}" for h in context_msgs[-3:]])
        
        payload = {
            "model": "llama3.1:8b",
            "prompt": f"GEÇMİŞ DİYALOGLAR:\n{history_str}\n\nİSTEK: {prompt}\nTomi:",
            "stream": False,
            "options": {"temperature": 0.1}
        }
        try:
            res = requests.post(OLLAMA_URL, json=payload, timeout=120)
            return res.json().get('response', '').strip()
        except: return ""

    def autonomous_learn(self, task, context_msgs):
        """5 Denemeli İleri Seviye Otomatik Tamirat Döngüsü."""
        skill_id = re.sub(r'\W+', '_', task).lower()
        if len(skill_id) > 50: skill_id = skill_id[:50]
        skill_path = os.path.join(SKILLS_DIR, f"{skill_id}.py")
        
        last_error = ""
        for attempt in range(1, 6):
            # 1. ARAŞTIRMA (Bağlamı kullanarak neyi araştırması gerektiğini anlar)
            research_data = ""
            if attempt == 1:
                search_query = self.think(f"Bu isteği gerçekleştirmek için ne aramalıyım? Sadece arama terimini yaz: {task}", context_msgs)
                try:
                    with DDGS() as ddgs:
                        results = list(ddgs.text(search_query, max_results=3))
                        research_data = "\n".join([r['body'] for r in results])
                except: pass

            # 2. KODLA / TAMİR ET (Hatayı bizzat LLM'e sorarak tamir ettirir)
            repair_prompt = ""
            if last_error:
                repair_prompt = f"\nAZ ÖNCEKİ KOD ŞU HATAYI VERDİ:\n{last_error}\nLÜTFEN BU HATAYI GİDEREREK KODU YENİDEN YAZ."

            prompt = (
                f"GÖREV: '{task}'\n"
                f"BAĞLAM VE ARAŞTIRMA: {research_data}\n{repair_prompt}\n"
                "KESİN KURALLAR:\n"
                "1. Sadece Python kodu ver.\n"
                "2. 'execute()' fonksiyonu olsun.\n"
                "3. Çıktı formatı 'SONUÇ: [veri]' olmalı.\n"
                "4. IP'den konum bulma gibi işlerde requests veya geocoder kullan."
            )
            
            raw_code = self.think(prompt, context_msgs)
            clean_code = re.sub(r"```python|```", "", raw_code).strip()
            
            with open(skill_path, "w", encoding="utf-8") as f:
                f.write(clean_code)

            # 3. TEST VE OTOMATİK KÜTÜPHANE KURULUMU
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

        return "Bu yetenek şu an için kullanılamadı, Hakan. (5 deneme başarısız)"

    def process(self, req):
        # Aksiyon kelimeleri süzgeci
        action_keywords = ["bak", "bul", "öğren", "hesapla", "incele", "getir", "yaz", "çalıştır", "listele", "söyle"]
        is_action = any(word in req.lower() for word in action_keywords)

        # 1. Bilinen Yetenek Kontrolü
        for skill, path in self.memory["learned_skills"].items():
            if skill.lower() in req.lower():
                res = subprocess.run([sys.executable, path, req], capture_output=True, text=True)
                if res.returncode == 0: return res.stdout.strip()

        # 2. Karar Mekanizması (Bağlamla birlikte)
        if is_action:
            return self.autonomous_learn(req, self.memory["history"])
        
        # 3. Sohbet ve Hafıza Kaydı
        response = self.think(req, self.memory["history"])
        self.memory["history"].append({"q": req, "a": response, "t": datetime.now().isoformat()})
        if len(self.memory["history"]) > 20: self.memory["history"] = self.memory["history"][-20:]
        
        return response

    def run(self):
        print(f"\n🌍 HW DAĞITIK BİLİNÇ v3.2 (TAMİRAT & BAĞLAM AKTİF)")
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
