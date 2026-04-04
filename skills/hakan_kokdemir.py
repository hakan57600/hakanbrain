import json
import os

MEMORY_FILE = os.path.expanduser("~/hakan_memory.json")

def profili_yukle():
    """Hakan KÖKDEMİR profil verilerini hafızadan yükler."""
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("hakan_profili", {})
        except: pass
    return {}

def profili_kaydet(profil):
    """Güncellenmiş profili hafızaya mühürler."""
    data = {"doğrular": {}, "yetenekler": {}, "hakan_profili": profil}
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                data["hakan_profili"] = profil
        except: pass
    
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def hakan_bilgi_ekle(kategori, bilgi):
    """
    Belirli bir kategoride (yemek, hobi, meslek vb.) bilgi ekler veya günceller.
    Örnek: hakan_bilgi_ekle("yemek_aliskanliklari", "Acılı yemekleri sever.")
    """
    profil = profili_yukle()
    if kategori not in profil:
        profil[kategori] = []
    
    if bilgi not in profil[kategori]:
        profil[kategori].append(bilgi)
        profili_kaydet(profil)
        return f"Hakan Bey'in '{kategori}' bilgisi güncellendi: {bilgi}, Hakan Bey."
    return f"Bu bilgi zaten hafızada mevcut, Hakan Bey."

def hakan_bilgi_getir(kategori=None):
    """Profil bilgilerini raporlar."""
    profil = profili_yukle()
    if kategori:
        return profil.get(kategori, f"Hakan Bey'in '{kategori}' kategorisinde henüz bir bilgi yok, Hakan Bey.")
    return profil

if __name__ == "__main__":
    # Test amaçlı ilk veriyi ekleyelim
    print(hakan_bilgi_ekle("kimlik", "Adı: Hakan, Soyadı: KÖKDEMİR"))
