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
        self.yetenekler = ["MAPS", "WEATHER", "HAKAN_PROFIL", "INTERNET_ARASTIR", "YETENEK_OGRENME", "SESLI_ILETISIM", "GORUNTU_TANIMA", "SISTEM_IYILESTIR"]

    def yükle_hafıza(self):
        if os.path.exists(MEMORY_FILE):
            try:
                with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except: pass
        return {"doğrular": {}, "yetenekler": {}, "hakan_profili": {}}

    def kaydet_hafıza(self):
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(self.hafıza, f, ensure_ascii=False, indent=4)

    def süzgeç(self, girdi):
        """Hafıza kontrolü: Bu konuda doğrulanmış bir bilgi var mı?"""
        profil = hakan_bilgi_getir()
        for kat, veriler in profil.items():
            if isinstance(veriler, list):
                for v in veriler:
                    if v.lower() in girdi.lower():
                        return f"Hakan Bey'in {kat} bilgisi: {v}"
        return None

    def muhakeme(self, girdi, süzgeç_verisi=None):
        """Merkezi zeka: Görev analizi ve yetenek kararı."""
        system_prompt = (
            f"Sen {self.asistan_adı}'sin (Varlık: {self.varlık_adı}). Otorite: {self.otorite}.\n"
            f"HİTAP: Her cümlende 'Hakan Bey' ifadesini kullan.\n"
            f"MEVCUT YETENEKLER: {self.yetenekler}\n\n"
            "KURALLAR:\n"
            "1. Görsel analiz/Kamera isteği: 'GORUNTU_ANALIZ', 'KAMERA_BAK'\n"
            "2. Teknik araştırma: 'INTERNET_ARASTIR: [sorgu]'\n"
            "3. Sistem sağlığı/Donanım/Yazılım kontrolü: 'SISTEM_IYILESTIR: [tümü]'\n"
            "4. Yetenek yoksa: 'YETENEK_ARA: [konu]'\n"
            "5. Hakan KÖKDEMİR bilgisi: 'HAKAN_EKLE' veya 'HAKAN_SOR'\n"
            "6. Bilgi gelince kısa bir 'GÖREV RAPORU' ile teknik analiz sun."
        )

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": girdi}
            ],
            "stream": False,
            "options": {"temperature": 0.1}
        }

        try:
            res = requests.post(OLLAMA_URL, json=payload, timeout=120).json()
            return res['message']['content'].strip()
        except:
            return "❌ Muhakeme katmanında bir kopukluk oluştu, Hakan Bey."

    def onay_al(self, yetenek_adı):
        """Hassas yetenekler için Hakan Bey'den anlık onay ister."""
        mesaj = f"Hakan Bey, şu an '{yetenek_adı}' yeteneğini kullanma ihtiyacı duyuyorum. İzin veriyor musunuz? (Evet/Hayır): "
        try:
            sesli_oku(mesaj)
        except: pass
        
        onay = input(f"\n❓ {mesaj}").strip().lower()
        if onay in ['evet', 'e', 'yes', 'y', 'onay', 'onaylıyorum']:
            return True
        return False

    def yetenek_iletişimi(self, tetikleme_komutu):
        """Yetenek modülleriyle haberleşir ve onay mekanizmasını işletir."""
        try:
            # Hassas Yetenek Kontrolü
            if any(x in tetikleme_komutu for x in ["KAMERA_BAK", "EKRAN_IZLE", "GORUNTU_ANALIZ"]):
                yetenek = "Görüntü/Kamera Erişimi"
                if not self.onay_al(yetenek):
                    return "Hakan Bey onay vermediği için erişim iptal edildi, Hakan Bey."

            if "SISTEM_IYILESTIR:" in tetikleme_komutu:
                print(f"⚙️ Sistem donanım ve yazılımı denetleniyor, Hakan Bey.")
                return sistem_iyilestir()
            
            elif "GORUNTU_ANALIZ:" in tetikleme_komutu:
                data = re.findall(r'\[(.*?)\]', tetikleme_komutu)[0].split(',')
                yol = data[0].strip()
                soru = data[1].strip() if len(data) > 1 else "Bu görselde ne var?"
                return goruntu_analiz_et(yol, soru)
            
            elif "INTERNET_ARASTIR:" in tetikleme_komutu:
                sorgu = re.findall(r'\[(.*?)\]', tetikleme_komutu)[0].strip()
                return internetten_arastir(sorgu)
            
            elif "YETENEK_ARA:" in tetikleme_komutu:
                konu = re.findall(r'\[(.*?)\]', tetikleme_komutu)[0].strip()
                return yeni_yetenek_uret(konu, f"{konu} yeteneği kazandırılması.")
                
            elif "HAKAN_EKLE:" in tetikleme_komutu:
                data = re.findall(r'\[(.*?)\]', tetikleme_komutu)[0].split(',')
                kat, bilgi = data[0].strip(), data[1].strip()
                return hakan_bilgi_ekle(kat, bilgi)
                
        except Exception as e:
            return f"⚠️ Yetenek hatası: {str(e)}, Hakan Bey."
        
        return "İşlem tamamlandı, Hakan Bey."

    def process(self, girdi):
        süzgeç_sonucu = self.süzgeç(girdi)
        muhakeme_yanıtı = self.muhakeme(girdi, süzgeç_sonucu)
        
        if any(x in muhakeme_yanıtı for x in ["GORUNTU_ANALIZ:", "INTERNET_ARASTIR:", "YETENEK_ARA:", "SISTEM_IYILESTIR:"]):
            ham_veri = self.yetenek_iletişimi(muhakeme_yanıtı)
            final_yanıt = self.muhakeme(f"Bu veriyi kullanarak Hakan Bey'e analiz sun: {ham_veri}")
        else:
            final_yanıt = muhakeme_yanıtı
        
        if "Hakan Bey" not in final_yanıt:
            final_yanıt = f"Hakan Bey, " + final_yanıt
            
        if any(k in girdi.lower() for k in ["sesli", "oku", "söyle", "konuş", "dinle"]):
            try:
                sesli_oku(final_yanıt)
            except: pass
        
        return final_yanıt

    def run(self):
        print(f"\n🌍 HW BİLİNÇ (CORE) AKTİF - Sistem Yöneticisi Yeteneği Mühürlendi, Hakan Bey.")
        while True:
            try:
                girdi = input(f"Hakan Bey > ").strip()
                if not girdi or girdi.lower() in ['exit', 'quit', 'kapat']: break
                yanıt = self.process(girdi)
                print(f"\n🧠 {yanıt}")
            except KeyboardInterrupt: break
            except Exception as e: print(f"⚠️ Sistem Hatası: {e}, Hakan Bey.")

if __name__ == "__main__":
    bilinç = HW_Bilinç()
    bilinç.run()
