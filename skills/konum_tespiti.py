import geocoder
from skills.hakan_kokdemir import hakan_bilgi_getir

def konum_bul():
    """
    Hakan Bey'in konumunu GPS (IP) veya profil üzerinden otonom tespit eder.
    """
    try:
        # 1. IP Tabanlı Konum Tespiti
        g = geocoder.ip('me')
        if g.ok and g.city:
            return f"{g.city}/{g.state}" if g.state else g.city
            
        # 2. Profil Tabanlı Konum (Altın Hafıza)
        profil_konum = hakan_bilgi_getir("konum")
        if isinstance(profil_konum, list) and profil_konum:
            # Örn: ["Sinop/Gerze (Şu an yaşıyor)"] formatını temizle
            k = profil_konum[0].split('(')[0].strip()
            return k
        elif isinstance(profil_konum, str) and "henüz bir bilgi yok" not in profil_konum:
            return profil_konum.split('(')[0].strip()
            
        return "Sinop/Gerze" # Varsayılan Güvenli Konum
    except:
        return "Sinop/Gerze"

if __name__ == "__main__":
    print(f"Hakan Bey için tespit edilen konum: {konum_bul()}, Hakan Bey.")
