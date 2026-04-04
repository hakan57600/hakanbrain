import requests

def get_weather(city):
    """
    Belirtilen şehir için hava durumunu çeker ve Hakan Bey'e özel tavsiyeler ekler.
    """
    try:
        # wttr.in üzerinden detaylı veri al
        url = f"https://wttr.in/{city}?format=%C+%t+%w+%p&lang=tr"
        response = requests.get(url, timeout=15)
        
        if response.status_code == 200:
            ham_veri = response.text.strip()
            # Örn ham_veri: "Bulutlu +8°C ↖15km/h 0.0mm"
            
            # Tavsiye Motoru
            tavsiye = ""
            temp_match = __import__('re').search(r'([-+]?\d+)', ham_veri)
            if temp_match:
                derece = int(temp_match.group(1))
                if derece < 12:
                    tavsiye += " Hava oldukça serin, Mondial Nevada motorunuzla çıkacaksanız sıkı giyinmeyi unutmayın, Hakan Bey. "
                elif derece > 30:
                    tavsiye += " Hava çok sıcak, bol su almayı ve güneşten korunmayı unutmayın, Hakan Bey. "
            
            if any(x in ham_veri.lower() for x in ["yağmur", "sağanak", "kar", "çisenti"]):
                tavsiye += " Yağış bekleniyor, motor kullanırken zemin kaygan olabilir, lütfen dikkat edin, Hakan Bey. "
            
            if not tavsiye:
                tavsiye = " Hava yolculuk için oldukça müsait görünüyor, keyfini çıkarın Hakan Bey."

            return f"{city} için durum: {ham_veri}.\n💡 Tavsiyem: {tavsiye}"
        else:
            return f"Üzgünüm Hakan Bey, {city} için hava durumu şu an alınamadı."
            
    except Exception as e:
        return f"⚠️ Hava durumu hatası: {str(e)}, Hakan Bey."

if __name__ == "__main__":
    print(get_weather("Sinop"))
