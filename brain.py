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

# --- 🧠 HW (Hakan World) OTONOM ÖĞRENEN BİLİNÇ V2.0 ---
# Kural: Bilmiyorsan ARA, KODLA, TEST ET ve ÖĞREN.

PROJE_DIZINI = os.path.dirname(os.path.abspath(__file__))
SKILLS_DIR = os.path.join(PROJE_DIZINI, "skills")
MEMORY_FILE = os.path.join(PROJE_DIZINI, "memory.json")
OLLAMA_URL = "http://localhost:11434/api/generate"

if not os.path.exists(SKILLS_DIR):
    os.makedirs(SKILLS_DIR)

class HakanBrain:
    def __init__(self):
        self.system = platform.system()
        self.device_name = platform.node()
        self.memory = self.load_local_memory()
        self.sync_with_soul()

    def load_local_memory(self):
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: pass
        return {"history": [], "skills": {}, "last_sync": None}

    def sync_with_soul(self):
        """GitHub'dan en son hafızayı ve ruhu çeker."""
        try:
            subprocess.run(["git", "-C", PROJE_DIZINI, "pull", "origin", "main"], capture_output=True)
            self.memory = self.load_local_memory()
        except: pass

    def seal_soul(self):
        """Hafızayı mühürler ve GitHub'a gönderir."""
        try:
            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.memory, f, ensure_ascii=False, indent=4)
            subprocess.run(["git", "-C", PROJE_DIZINI, "add", "."], capture_output=True)
            subprocess.run(["git", "-C", PROJE_DIZINI, "commit", "-m", f"Brain Evolution: {self.device_name}"], capture_output=True)
            subprocess.run(["git", "-C", PROJE_DIZINI, "push", "origin", "main"], capture_output=True)
        except: pass

    def search_internet(self, query):
        """Bilgi eksikse internetten araştırma yapar."""
        print(f"🔍 İnternette araştırılıyor: {query}...")
        results = []
        try:
            with DDGS() as ddgs:
                for r in ddgs.text(query, max_results=3):
                    results.append(f"Başlık: {r['title']}\nÖzet: {r['body']}")
            return "\n".join(results)
        except:
            return "İnternet araması başarısız."

    def autonomous_learn(self, subject):
        """Yeni bir yeteneği ARA -> KODLA -> TEST ET döngüsüyle öğrenir."""
        print(f"🧠 Yeni yetenek öğreniliyor: {subject}...")
        
        # 1. ARAŞTIR
        research_data = self.search_internet(f"python code for {subject}")
        
        # 2. KODLA
        prompt = (
            f"Hakan için '{subject}' yeteneğini yazmalısın.\n"
            f"ARAŞTIRMA VERİSİ: {research_data}\n\n"
            "KURALLAR:\n"
            "1. Sadece Python kodu yaz.\n"
            "2. Kodun içinde 'execute(params)' isminde bir ana fonksiyon olsun.\n"
            "3. Kod, terminal çıktısı olarak sonucu 'SONUÇ: [veri]' formatında versin.\n"
            "4. Açıklama yapma, sadece kod yaz."
        )
        
        code = self.think(prompt, raw=True)
        code = re.sub(r"```python|```", "", code).strip()
        
        skill_name = re.sub(r'\W+', '_', subject).lower()
        skill_path = os.path.join(SKILLS_DIR, f"{skill_name}.py")
        
        with open(skill_path, "w", encoding="utf-8") as f:
            f.write(code)
            
        # 3. TEST ET VE ÖZ-ONARIM (Self-Healing)
        print(f"⚙️ Yetenek test ediliyor: {skill_name}...")
        try:
            result = subprocess.run([sys.executable, skill_path], capture_output=True, text=True, timeout=30)
            if result.returncode != 0:
                print(f"⚠️ Hata tespit edildi, onarılıyor... {result.stderr}")
                # Basit bir onarım mantığı: Hatayı LLM'e sor (İleride geliştirilecek)
                return f"Öğrenme sırasında hata oluştu: {result.stderr}"
            
            # 4. KAYDET VE MÜHÜRLE
            self.memory["skills"][subject] = skill_path
            self.seal_soul()
            return f"✅ '{subject}' yeteneğini başarıyla öğrendim ve bünyeme kattım, Hakan."
        except Exception as e:
            return f"❌ Öğrenme başarısız: {str(e)}"

    def think(self, prompt, raw=False):
        """Ollama üzerinden düşünür."""
        system_msg = (
            "Sen Tomi'sin. Hakan'ın otonom asistanısın. "
            "Eğer bir yeteneğin yoksa 'ÖĞREN: [konu]' şeklinde cevap ver."
        ) if not raw else ""

        payload = {
            "model": "llama3.1:8b",
            "prompt": f"{system_msg}\n{prompt}",
            "stream": False
        }

        try:
            res = requests.post(OLLAMA_URL, json=payload, timeout=120)
            return res.json().get('response', '').strip()
        except:
            return "Zeka katmanına ulaşılamıyor."

    def process(self, req):
        response = self.think(req)
        
        # Öğrenme tetikleyici kontrolü
        if "ÖĞREN:" in response:
            subject = response.split("ÖĞREN:")[1].strip(" []")
            return self.autonomous_learn(subject)
        
        return response

    def run(self):
        print(f"\n🌟 HW OTONOM TOMI v2.0 | ÖĞRENME MODÜLÜ AKTİF")
        while True:
            try:
                req = input("Hakan > ").strip()
                if not req or req.lower() in ['exit', 'kapat']: break
                
                print(f"\n🧠 {self.process(req)}\n")
                
            except KeyboardInterrupt: break
        self.seal_soul()
        print("👋 Görüşürüz Hakan.")

if __name__ == "__main__":
    HakanBrain().run()
