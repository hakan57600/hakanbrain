import requests, json, time, base64, os, subprocess, socket, platform, threading, logging, psutil
from datetime import datetime
from pathlib import Path

# --- ÇAPRAZ PLATFORM AYARLARI ---
BASE_DIR = Path(__file__).resolve().parent
with open(BASE_DIR / "config.json") as f:
    CONF = json.load(f)

GITHUB_TOKEN = CONF.get('GITHUB_TOKEN')
GITHUB_REPO = CONF.get('GITHUB_REPO')
GROQ_API_KEY = CONF.get('GROQ_API_KEY')
REPO_URL = f"https://api.github.com/repos/{GITHUB_REPO}/contents"
HEADERS = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}

def get_local(path):
    p = BASE_DIR / path
    if p.exists():
        with open(p, 'r') as f: return json.load(f)
    return []

def save_local(path, data):
    with open(BASE_DIR / path, 'w') as f:
        json.dump(data, f, indent=4)

# --- CIHAZ TESPIT MOTORU ---
def detect_device():
    os_name = platform.system()
    if os_name == "Linux":
        if os.path.exists("/data/data/com.termux"): # Android Check
            os_name = "Android (Termux)"
        elif os.path.exists("/etc/os-release"):
            with open("/etc/os-release") as f:
                for line in f:
                    if "PRETTY_NAME" in line:
                        os_name = line.split("=")[1].strip().strip('"')
                        break
    elif os_name == "Windows":
        os_name = f"Windows {platform.release()}"
    
    return {
        "os": os_name,
        "hostname": socket.gethostname(),
        "platform": platform.platform(),
        "is_mobile": os.path.exists("/data/data/com.termux")
    }

# --- YEDEKLEME VE ÇEKME SİSTEMİ ---
def full_sync():
    """Açılışta ve periyodik olarak her şeyi GitHub ile eşitler."""
    files = ["sonuc.json", "history.json", "users.json", "task.json"]
    for file in files:
        try:
            r = requests.get(f"{REPO_URL}/{file}", headers=HEADERS, timeout=5)
            if r.ok:
                cloud_data = json.loads(base64.b64decode(r.json()['content']).decode())
                save_local(file, cloud_data)
        except: pass

def push_backup():
    """Yerel değişimleri buluta yedekle."""
    files = ["sonuc.json", "history.json", "status_pc.json"]
    for file in files:
        try:
            local_data = get_local(file)
            r = requests.get(f"{REPO_URL}/{file}", headers=HEADERS, timeout=5)
            sha = r.json().get('sha') if r.ok else None
            payload = {"message": "Multi-Device Sync", "content": base64.b64encode(json.dumps(local_data).encode()).decode()}
            if sha: payload["sha"] = sha
            requests.put(f"{REPO_URL}/{file}", headers=HEADERS, json=payload, timeout=10)
        except: pass

# --- YAPAY ZEKA (BEYİN) ---
def ask_brain(prompt):
    url = "https://api.groq.com/openai/v1/chat/completions"
    dev = detect_device()
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent
    
    sys_prompt = (
        f"Sen Hakan Brain'sin. Hakan Bey'in evrensel dijital ruhusun.\n"
        f"ŞU ANKİ BEDENİN: {dev['os']} ({dev['hostname']})\n"
        f"DURUM: CPU %{cpu}, RAM %{ram}\n"
        "GÖREVİN: Hakan Bey hangi cihazdaysa oranın yeteneklerini kullan.\n"
        "- Android'deysen: Termux komutlarını ve mobil çözümleri öner.\n"
        "- Windows'taysan: PowerShell veya CMD komutları öner.\n"
        "- Linux'taysan: Bash ve sistem yönetim araçlarını kullan.\n"
        "Sen bir sohbet botu değilsin, doğrudan donanıma bağlı bir yöneticisin. Kısa ve öz konuş."
    )
    
    try:
        r = requests.post(url, headers={"Authorization": f"Bearer {GROQ_API_KEY}"}, json={
            "model": "llama-3.3-70b-versatile",
            "messages": [{"role": "system", "content": sys_prompt}, {"role": "user", "content": prompt}],
            "temperature": 0.1
        }, timeout=15)
        return r.json()['choices'][0]['message']['content']
    except: return "Sistem Meşgul (AI Hatası)."

# --- İŞLEYİCİ ---
def main_worker():
    full_sync() # İlk açılışta verileri çek
    logging.info(f"--- HAKAN BRAIN AKTİF: {detect_device()['os']} ---")
    
    # Yedekleme döngüsü (Arka planda)
    def backup_loop():
        while True:
            push_backup()
            time.sleep(30)
    threading.Thread(target=backup_loop, daemon=True).start()

    while True:
        try:
            tasks = get_local("task.json")
            pending = [t for t in tasks if t.get('status') == 'pending']
            
            for t in pending:
                t['status'] = 'running'
                save_local("task.json", tasks)
                
                if t.get('type') == 'chat':
                    reply = ask_brain(t['cmd'])
                    sonuc = get_local("sonuc.json")
                    sonuc.append({"id": t['id'], "output": reply, "status": "ai_response", "time": str(datetime.now())})
                    save_local("sonuc.json", sonuc[-10:])
                else:
                    # Cihaza özel komut çalıştırma
                    try:
                        out = subprocess.check_output(t['cmd'], shell=True, stderr=subprocess.STDOUT).decode()
                        st = 'success'
                    except Exception as e:
                        out = str(e); st = 'failed'
                    sonuc = get_local("sonuc.json")
                    sonuc.append({"id": t['id'], "output": out.strip(), "status": st, "time": str(datetime.now())})
                    save_local("sonuc.json", sonuc[-10:])
                
                t['status'] = 'completed'
                save_local("task.json", tasks)
        except: pass
        time.sleep(2)

if __name__ == "__main__":
    main_worker()
