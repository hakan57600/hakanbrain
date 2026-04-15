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

# --- 🧠 HAKAN WORLD V5.0 ---
# Kural: Akıllı Ayrım (Sohbet/İşlem), Sessiz Tamirat (5 Deneme), OpenClaw Uyumu.

warnings.filterwarnings("ignore")

PROJE_DIZINI = os.path.dirname(os.path.abspath(__file__))
SKILLS_DIR = os.path.join(PROJE_DIZINI, "skills")
MEMORY_FILE = os.path.join(PROJE_DIZINI, "memory.json")
OLLAMA_URL = "http://localhost:11434/api/generate"

if not os.path.exists(SKILLS_DIR): os.makedirs(SKILLS_DIR)

class HakanWorld:
    def __init__(self):
        self.device = platform.node()
        self.memory = self.load_memory()

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

    def push_soul(self):
        try:
            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.memory, f, ensure_ascii=False, indent=4)
            subprocess.run(["git", "-C", PROJE_DIZINI, "add", "."], capture_output=True)
            subprocess.run(["git", "-C", PROJE_DIZINI, "commit", "-m", f"HW V5 Update: {self.device}"], capture_output=True)
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
        except: return ""

    def autonomous_learn(self, task):
        """Sessizce öğren ve 5 denemede tamir et."""
        skill_id = re.sub(r'\W+', '_', task).lower()[:50]
        skill_path = os.path.join(SKILLS_DIR, f"{skill_id}.py")
        
        last_error = ""
        for attempt in range(1, 6):
            research = ""
            if attempt == 1:
                try:
                    with DDGS() as ddgs:
                        results = list(ddgs.text(f"python code to {task}", max_results=2))
                        research = "\n".join([r['body'] for r in results])
                except: pass

            repair = f"\nÖnceki Hata: {last_error}" if last_error else ""
            prompt = (
                f"GÖREV: {task}\nARAŞTIRMA: {research}\n{repair}\n"
                "KURAL: Sadece Python kodu. execute() olsun. Çıktı 'SONUÇ: [veri]' olmalı."
            )
            raw_code = self.think(prompt, "Sen bir yazılım mühendisisin. Sadece kod ver.")
            clean_code = re.sub(r"```python|```", "", raw_code).strip()
            
            with open(skill_path, "w", encoding="utf-8") as f:
                f.write(clean_code)

            test = subprocess.run([sys.executable, skill_path], capture_output=True, text=True)
            if test.returncode == 0:
                self.memory["learned_skills"][task] = skill_path
                return test.stdout.strip()
            else:
                last_error = test.stderr
                if "ModuleNotFoundError" in last_error:
                    lib = last_error.split("'")[1]
                    subprocess.run([sys.executable, "-m", "pip", "install", lib], capture_output=True)
                continue
        return "İşlem başarısız oldu."

    def process(self, req):
        # 1. Hızlı Filtre: Sohbet mi İşlem mi?
        action_words = ["nerede", "bul", "kaç", "öğren", "hesapla", "çalıştır", "hava", "fiyat"]
        is_action = any(w in req.lower() for w in action_words)

        if is_action:
            # Bilinen yetenek?
            for skill, path in self.memory["learned_skills"].items():
                if skill.lower() in req.lower():
                    res = subprocess.run([sys.executable, path], capture_output=True, text=True)
                    return res.stdout.strip() if res.returncode == 0 else "Hata oluştu."
            return self.autonomous_learn(req)
        
        # 2. Sohbet (Hızlı)
        return self.think(req, "Sen Hakan'ın asistanı Tomi'sin. Kısa ve zeki cevap ver.")

    def run(self):
        print(f"\n🌍 HAKAN WORLD V5.0")
        while True:
            try:
                req = input("\nHakan > ").strip()
                if not req or req.lower() in ['exit', 'kapat']: break
                response = self.process(req)
                print(f"\n🧠 {response}")
            except KeyboardInterrupt: break
        self.push_soul()

if __name__ == "__main__":
    HakanWorld().run()
