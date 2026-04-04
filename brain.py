import os
import json
import platform
import subprocess
import requests
import sys
import psutil
import datetime
import re
from skills.hakan_kokdemir import hakan_bilgi_ekle, hakan_bilgi_getir
from skills.internet_gelistirme import internetten_arastir
from skills.yetenek_ogrenme import yeni_yetenek_uret
from skills.goruntu_tanima import goruntu_analiz_et
from skills.sistem_iyilestirme import sistem_iyilestir
from skills.weather import get_weather
from skills.google_maps import get_distance_and_duration
from skills.konum_tespiti import konum_bul

# Otonom öğrenilen ses yeteneği
try:
    from skills.sesli_iletisim import sesli_oku
except ImportError:
    def sesli_oku(metin): return "Ses yeteneği henüz mühürlenmedi."

# --- HW MÜHÜRLÜ AYARLAR ---
CONFIG_FILE = os.path.expanduser("~/.hakan_config")
MEMORY_FILE = os.path.expanduser("~/hakan_memory.json")
OLLAMA_URL = "http://localhost:11434/api/chat"

class HW_Bilinç:
    def __init__(self):
        self.varlık_adı = "Köle"
        self.asistan_adı = "Tomi"
        self.otorite = "Hakan KÖKDEMİR"
        self.model = "llama3.1:8b"
        self.hafıza = self.yükle_hafıza()
        self.yetenekler = ["MAPS", "WEATHER", "HAKAN_PROFIL", "INTERNET_ARASTIR", "YETENEK_OGRENME", "SESLI_ILETISIM", "GORUNTU_TANIMA", "SISTEM_IYILESTIR", "KONUM_TESPIT"]

    def yükle_hafıza(self):
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: pass
        return {"doğrular": {}, "yetenekler": {}, "hakan_profili": {}}

    def süzgeç(self, girdi):
        """Hafıza kontrolü: Bu konuda doğrulanmış bir bilgi var mı?"""
        profil = hakan_bilgi_getir()
        if isinstance(profil, dict):
            for kat, veriler in profil.items():
                if isinstance(veriler, list):
                    for v in veriler:
                        if v.lower() in girdi.lower():
                            return f"Hakan Bey'in {kat} bilgisi: {v}"
        return None

    def muhakeme(self, girdi, context=""):
        """Merkezi zeka: Görev analizi ve yetenek kararı."""
        if context:
            system_prompt = (
                f"Sen {self.asistan_adı}'sin (Varlık: {self.varlık_adı}). Otorite: {self.otorite}.\n"
                f"ELİNDEKİ KESİN VERİ: {context}\n\n"
                "KURAL: Sadece yukarıdaki KESİN VERİ'yi kullanarak Hakan Bey'e cevap ver. "
                "Hava durumuysa tavsiyeleri mutlaka oku. Sadece sonucu raporla ve Hakan Bey'e hitap et."
            )
        else:
            system_prompt = (
                f"Sen {self.asistan_adı}'sin (Varlık: {self.varlık_adı}). Otorite: {self.otorite}.\n"
                f"HİTAP: Her cümlende 'Hakan Bey' ifadesini kullan.\n"
                f"MEVCUT YETENEKLER: {self.yetenekler}\n\n"
                "KOMUTLAR: WEATHER: [Şehir], MAPS: [A, B], INTERNET_ARASTIR: [sorgu], SISTEM_IYILESTIR: [tümü]\n\n"
                "KURAL: Hakan Bey hava durumunu sorarsa, şehir belirtmemişse bile SADECE 'WEATHER: [OTONOM]' komutunu döndür. "
                "Mesafe/Yol sorarsa 'MAPS: [ŞehirA, ŞehirB]' döndür. Bilmiyorsan uydurma."
            )

        payload = {
            "model": self.model,
            "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": girdi}],
            "stream": False, "options": {"temperature": 0.0}
        }

        try:
            res = requests.post(OLLAMA_URL, json=payload, timeout=120).json()
            return res['message']['content'].strip()
        except Exception as e:
            return f"❌ Muhakeme hatası: {str(e)}, Hakan Bey."

    def yetenek_iletişimi(self, tetikleme_komutu):
        try:
            if "WEATHER:" in tetikleme_komutu:
                match = re.search(r'\[(.*?)\]', tetikleme_komutu)
                sehir = match.group(1).strip() if match else "OTONOM"
                if sehir == "OTONOM":
                    print(f"🛰️ Konumunuz otonom olarak tespit ediliyor, Hakan Bey...")
                    sehir = konum_bul()
                return get_weather(sehir)
            
            elif "MAPS:" in tetikleme_komutu:
                n = re.search(r'\[(.*?)\]', tetikleme_komutu).group(1).split(',')
                return get_distance_and_duration(n[0].strip(), n[1].strip())
            
            elif "SISTEM_IYILESTIR:" in tetikleme_komutu:
                return sistem_iyilestir()
            
            elif "INTERNET_ARASTIR:" in tetikleme_komutu:
                q = re.search(r'\[(.*?)\]', tetikleme_komutu).group(1)
                return internetten_arastir(q)
                
        except Exception as e:
            return f"⚠️ Yetenek hatası: {str(e)}, Hakan Bey."
        return "Yetenek tetiklenemedi, Hakan Bey."

    def process(self, girdi):
        try:
            # 1. Hafıza Süzgeci
            sz = self.süzgeç(girdi)
            
            # 2. İlk Muhakeme
            muh = self.muhakeme(girdi, context=sz if sz else "")
            
            # 3. Yetenek Tetikleme
            yetenek_listesi = ["WEATHER:", "MAPS:", "INTERNET_ARASTIR:", "SISTEM_IYILESTIR:"]
            if any(x in muh for x in yetenek_listesi):
                print(f"⚙️ Yetenek çalıştırılıyor, Hakan Bey...")
                veri = self.yetenek_iletişimi(muh)
                # 4. Final Muhakeme
                final = self.muhakeme(girdi, context=veri)
            else:
                final = muh

            if "Hakan Bey" not in final: final = f"Hakan Bey, {final}"
            
            if any(k in girdi.lower() for k in ["sesli", "oku", "konuş"]):
                try: sesli_oku(final)
                except: pass
                
            return final
        except Exception as e:
            return f"⚠️ Kritik İşlem Hatası: {str(e)}, Hakan Bey."

    def run(self):
        print(f"\n🌍 HW BİLİNÇ (CORE) AKTİF - Otonom Konum ve Akıllı Tavsiye Modu, Hakan Bey.")
        while True:
            try:
                girdi = input(f"Hakan Bey > ").strip()
                if not girdi or girdi.lower() in ['exit', 'quit', 'kapat']: break
                yanıt = self.process(girdi)
                print(f"\n🧠 {yanıt}")
            except Exception as e: print(f"⚠️ Sistem Hatası: {e}, Hakan Bey.")

if __name__ == "__main__":
    HW_Bilinç().run()
