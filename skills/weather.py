import requests

def get_weather(city):
    """
    Belirtilen şehir için güncel hava durumu bilgisini döner.
    Kaynak: wttr.in (MGM vb. resmi kaynaklara alternatif olarak).
    Kural: AI rakam uyduramaz, sadece kaynaktan geleni söyler.
    """
    try:
        # wttr.in üzerinden sadeleştirilmiş hava durumu verisi al (format=3: "Şehir: Durum Sıcaklık")
        url = f"https://wttr.in/{city}?format=3&lang=tr"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            return response.content.decode('utf-8').strip()
        else:
            return f"Üzgünüm Hakan, {city} için hava durumu verisi şu an alınamadı."
            
    except Exception as e:
        return f"Hata oluştu: {str(e)}"

if __name__ == "__main__":
    # Test
    print(get_weather("Ankara"))
