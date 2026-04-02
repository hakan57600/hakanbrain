import os
import json
import platform
import subprocess
import requests
from github import Github

# --- AYARLAR ---
# Config dosyası masaüstüne oluşturulduğu için oradan okuyoruz
CONFIG_FILE = os.path.expanduser("~/Masaüstü/.hakan_config")
MEMORY_FILE = os.path.expanduser("~/Masaüstü/memory.json")
OLLAMA_URL = "http://localhost:11434/api/generate"

class HybridMemory:
    def __init__(self, token, repo_name):
        self.gh = Github(token)
        try:
            self.repo = self.gh.get_repo(repo_name)
        except Exception as e:
            print(f"❌ Repo bulunamadı: {repo_name}. Lütfen GitHub'da bu isimle bir repo oluşturun.")
            exit()
        self.local_data = self.load_local()

    def load_local(self):
        if os.path.exists(MEMORY_FILE):
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"history": [], "learned_commands": {}, "last_sync": None}

    def sync(self):
        print("🔄 GitHub ile senkronize ediliyor...")
        try:
            # GitHub'daki memory.json dosyasını kontrol et
            try:
                contents = self.repo.get_contents("memory.json")
                remote_data = json.loads(contents.decoded_content.decode())
                
                # Basit Merge (Birleştirme)
                remote_data["learned_commands"].update(self.local_data["learned_commands"])
                # Yeni geçmiş öğelerini ekle (tekrar etmeden)
                for item in self.local_data["history"]:
                    if item not in remote_data["history"]:
                        remote_data["history"].append(item)
                
                self.local_data = remote_data
                sha = contents.sha
            except:
                # Eğer GitHub'da memory.json yoksa ilk kez oluştur
                print("📝 GitHub'da memory.json oluşturuluyor...")
                sha = None

            # Yerel dosyayı güncelle
            with open(MEMORY_FILE, "w", encoding="utf-8") as f:
                json.dump(self.local_data, f, indent=4)
            
            # GitHub'a yükle
            content_str = json.dumps(self.local_data, indent=4)
            if sha:
                self.repo.update_file("memory.json", "Brain Sync: Güncelleme", content_str, sha)
            else:
                self.repo.create_file("memory.json", "Brain Sync: İlk Kurulum", content_str)
            
            print("✅ Senkronizasyon Tamamlandı!")
        except Exception as e:
            print(f"⚠️ Senkronizasyon Hatası (Offline Mod): {e}")

class HakanBrain:
    def __init__(self):
        self.token, self.user = self.load_config()
        self.repo_name = f"{self.user}/hakanbrain"
        self.memory = HybridMemory(self.token, self.repo_name)
        self.system = platform.system()

    def load_config(self):
        if not os.path.exists(CONFIG_FILE):
            print(f"❌ {CONFIG_FILE} bulunamadı!")
            exit()
        config = {}
        with open(CONFIG_FILE, "r") as f:
            for line in f:
                if "=" in line:
                    parts = line.strip().split("=", 1)
                    if len(parts) == 2:
                        config[parts[0]] = parts[1]
        return config.get("GITHUB_TOKEN"), config.get("GITHUB_USER")

    def think(self, prompt):
        print("🧠 Düşünülüyor...")
        system_msg = f"Sen Hakan'ın Linux/Windows/Android asistanısın. İşletim sistemi: {self.system}. Kullanıcının isteğine uygun TEK BİR terminal komutu üret. Açıklama yapma, sadece komutu yaz."
        
        try:
            payload = {
                "model": "llama3",
                "prompt": f"{system_msg}\nİstek: {prompt}\nKomut:",
                "stream": False
            }
            res = requests.post(OLLAMA_URL, json=payload, timeout=10)
            return res.json()['response'].strip().replace('`', '')
        except:
            return "Hata: Ollama servisinden cevap alınamadı. (ollama serve açık mı?)"

    def run(self):
        print(f"\n🌟 HAKAN BRAIN v3 AKTİF! [Sistem: {self.system}]")
        print("Çıkmak için 'exit' yazın.\n")
        
        while True:
            try:
                req = input("Hakan > ").strip()
                if not req: continue
                if req.lower() in ['exit', 'quit']: break
                
                cmd = self.think(req)
                print(f"🤖 Önerilen Komut: {cmd}")
                
                ans = input("✅ Onaylıyor musun? (e/h): ").lower()
                if ans == 'e':
                    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                    if result.returncode == 0:
                        print(f"--- ÇIKTI ---\n{result.stdout}")
                    else:
                        print(f"--- HATA ---\n{result.stderr}")
                    
                    self.memory.local_data["history"].append({"request": req, "command": cmd})
                    self.memory.sync()
                else:
                    print("⚠️ İşlem iptal edildi.")
                    
            except KeyboardInterrupt:
                break
        print("\n👋 Beyin uyku moduna geçiyor...")

if __name__ == "__main__":
    brain = HakanBrain()
    brain.run()
