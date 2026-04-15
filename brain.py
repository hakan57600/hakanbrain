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

# --- 🧠 HW (Hakan World) OTONOM ÖĞRENEN BİLİNÇ V2.1 ---
# Felsefe: Önce Araştır, Sonra Kodla, Test Et ve Hafızaya Mühürle.

PROJE_DIZINI = os.path.dirname(os.path.abspath(__file__))
SKILLS_DIR = os.path.join(PROJE_DIZINI, "skills")
MEMORY_FILE = os.path.join(PROJE_DIZINI, "memory.json")
OLLAMA_URL = "http://localhost:11434/api/generate"

# Klasör Güvenliği
if not os.path.exists(SKILLS_DIR):
    os.makedirs(SKILLS_DIR)

class TomiBrain:
    def __init__(self):
        self.system = platform.system()
        self.device = platform.node()
        self.memory = self.load_memory()
        self.sync_soul() # Açılışta GitHub'dan çek

    def load_memory(self):
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    if "learned_skills" not in data:
                        data["learned_skills"] = {}
                    return data
            except: pass
        return {"history": [], "learned_skills": {}, "last_sync": None}

    def sync_soul(self):
        """Ruhu GitHub'dan çeker (git pull)."""
        try:
            subprocess.run(["git", "-C", PROJE_DIZINI, "pull", "origin", "main"], capture_output=True)
            self.memory = self.load_memory()
        except: pass

    def push_soul(self):
        """Ruhu GitHub'a mühürler (git push)."""
        try:
            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.memory, f, ensure_ascii=False, indent=4)
            subprocess.run(["git", "-C", PROJE_DIZINI, "add", "."], capture_output=True)
            subprocess.run(["git", "-C", PROJE_DIZINI, "commit", "-m", f"Sync from {self.device}"], capture_output=True)
            subprocess.run(["git", "-C", PROJE_DIZINI, "push", "origin", "main"], capture_output=True)
        except: pass

    def think(self, prompt, system_prompt=""):
        """Ollama üzerinden düşünür."""
        payload = {
            "model": "llama3.1:8b",
            "prompt": f"{system_prompt}\n\nHakan: {prompt}\nTomi:",
            "stream": False,
            "options": {"temperature": 0.2}
        }
        try:
            res = requests.post(OLLAMA_URL, json=payload, timeout=120)
            return res.json().get('response', '').strip()
        except:
            return "Zeka katmanına ulaşılamıyor (Ollama kapalı mı?)."

    def execute_skill(self, skill_file, params=""):
        """Öğrenilmiş bir yeteneği çalıştırır."""
        try:
            result = subprocess.run([sys.executable, skill_file, params], capture_output=True, text=True)
            if result.returncode == 0:
                return result.stdout.strip()
            return f"Yetenek Hatası: {result.stderr}"
        except Exception as e:
            return f"Sistemsel Hata: {str(e)}"

    def autonomous_learn(self, task):
        """ARA -> KODLA -> TEST ET -> MÜHÜRLE döngüsü."""
        print(f"🔍 '{task}' görevi için internette araştırma yapılıyor...")
        
        # 1. ARAŞTIR
        research_context = ""
        try:
            with DDGS() as ddgs:
                results = list(ddgs.text(f"python code for {task}", max_results=3))
                research_context = "\n".join([r['body'] for r in results])
        except: research_context = "İnternete erişilemedi, genel bilgilerle kodlanacak."

        # 2. KODLA
        print(f"🛠️ Yetenek kodlanıyor...")
        code_prompt = (
            f"Sen bir Python uzmanısın. Hakan için şu görevi yapan bağımsız bir script yaz: '{task}'\n"
            f"Araştırma Notları: {research_context}\n\n"
            "KURALLAR:\n"
            "1. Sadece Python kodu ver, açıklama yapma.\n"
            "2. Gerekli kütüphaneleri (requests, bs4 vb.) import et.\n"
            "3. Sonucu mutlaka 'SONUÇ: [veri]' şeklinde yazdır.\n"
            "4. Kodun temiz ve hatasız olsun."
        )
        
        raw_code = self.think(code_prompt)
        clean_code = re.sub(r"```python|```", "", raw_code).strip()
        
        skill_id = re.sub(r'\W+', '_', task).lower()
        skill_path = os.path.join(SKILLS_DIR, f"{skill_id}.py")
        
        with open(skill_path, "w", encoding="utf-8") as f:
            f.write(clean_code)

        # 3. TEST ET VE KÜTÜPHANE KONTROLÜ
        print(f"⚙️ Yetenek test ediliyor...")
        test_run = subprocess.run([sys.executable, skill_path], capture_output=True, text=True)
        
        if "ModuleNotFoundError" in test_run.stderr:
            lib = test_run.stderr.split("'")[1]
            print(f"📦 Eksik kütüphane bulundu: {lib}. Kuruluyor...")
            subprocess.run([sys.executable, "-m", "pip", "install", lib], capture_output=True)
            test_run = subprocess.run([sys.executable, skill_path], capture_output=True, text=True) # Tekrar dene

        if test_run.returncode == 0:
            print(f"✅ Yetenek başarıyla öğrenildi: {task}")
            self.memory["learned_skills"][task] = skill_path
            self.push_soul()
            return test_run.stdout.strip()
        else:
            return f"❌ Öğrenme başarısız: {test_run.stderr}"

    def run(self):
        print(f"\n🌍 HW DAĞITIK TOMI v2.1 (OTONOM ÖĞRENME AKTİF)")
        print(f"Hafızadaki Yetenek Sayısı: {len(self.memory['learned_skills'])}")
        
        while True:
            try:
                req = input("\nHakan > ").strip()
                if not req or req.lower() in ['exit', 'kapat', 'çıkış']: break
                
                # Yetenek kontrolü
                found_skill = None
                for skill, path in self.memory["learned_skills"].items():
                    if skill.lower() in req.lower():
                        found_skill = path
                        break
                
                if found_skill:
                    print(f"⚙️ Bilinen yetenek tetikleniyor: {os.path.basename(found_skill)}")
                    print(f"\n🧠 {self.execute_skill(found_skill, req)}")
                else:
                    # Karar aşaması: Sohbet mi, yeni yetenek mi?
                    decision_prompt = (
                        "Kullanıcının isteği yeni bir 'fiziksel işlem' (hesaplama, veri çekme, dosya işlemi) mi gerektiriyor? "
                        "Evet ise sadece 'ÖĞREN' yaz. Hayır sadece sohbet ise normal cevap ver."
                    )
                    decision = self.think(req, system_prompt=decision_prompt)
                    
                    if "ÖĞREN" in decision.upper():
                        print(f"\n🧠 {self.autonomous_learn(req)}")
                    else:
                        print(f"\n🧠 {decision}")
                        
            except KeyboardInterrupt: break
        
        self.push_soul()
        print("\n👋 Hafıza GitHub'a mühürlendi. Görüşürüz Hakan.")

if __name__ == "__main__":
    TomiBrain().run()
