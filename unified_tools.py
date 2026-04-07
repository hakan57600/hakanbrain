import os
import subprocess
import requests
import webbrowser
import sys

# DÜZ YAPI MÜHÜRÜ
hakanbrain_dir = os.path.dirname(os.path.abspath(__file__))
if hakanbrain_dir not in sys.path:
    sys.path.insert(0, hakanbrain_dir)

from google_maps import get_distance_and_duration
from weather import get_weather

def tool_uygulama_kesfet_ve_ac(app_query):
    try:
        query = app_query.lower().strip()
        search_paths = ["/usr/share/applications", os.path.expanduser("~/.local/share/applications")]
        for path in search_paths:
            if not os.path.exists(path): continue
            for file in os.listdir(path):
                if not file.endswith(".desktop"): continue
                try:
                    with open(os.path.join(path, file), "r") as f:
                        content = f.read().lower()
                        if query in content:
                            for line in content.split("\n"):
                                if line.startswith("exec="):
                                    cmd = line.split("=")[1].split()[0].replace("%u", "").replace("%U", "").strip()
                                    subprocess.Popen(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                                    return f"Açtım Hakan: {file.replace('.desktop', '')}"
                except: continue
        return f"{app_query} bulunamadı."
    except: return "Uygulama açma hatası."

def tool_internet_ara_ve_ac(query):
    try:
        webbrowser.open(f"https://www.google.com/search?q={query}")
        return f"Tarayıcıda '{query}' açıldı."
    except: return "Tarayıcı hatası."

def tool_hava_durumu(sehir): return get_weather(sehir)
def tool_mesafe_hesapla(param):
    pts = param.replace('-', ' ').split()
    return get_distance_and_duration(pts[0], pts[1]) if len(pts) >= 2 else "Noktalar eksik."
