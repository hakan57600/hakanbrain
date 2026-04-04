import requests
from duckduckgo_search import DDGS
import re

def get_distance_and_duration(origin, destination):
    """
    Google Maps verilerini (veya en yakın arama sonuçlarını) kullanarak 
    iki nokta arası mesafe ve süre bilgisini döner.
    Kural: AI rakam uyduramaz, sadece kaynaktan geleni söyler.
    """
    query = f"{origin} {destination} arası kaç km kaç saat sürer google maps"
    
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))
            
        combined_text = " ".join([r['body'] for r in results])
        
        # Basit regex ile mesafe (km) ve süre (saat/dakika) ara
        distance_match = re.search(r'(\d+[\.,]?\d*)\s*(?:km|kilometre)', combined_text, re.IGNORECASE)
        duration_match = re.search(r'(\d+)\s*(?:saat|sa)\s*(\d+)?\s*(?:dakika|dk)?', combined_text, re.IGNORECASE)
        
        distance = distance_match.group(0) if distance_match else None
        duration = duration_match.group(0) if duration_match else None
        
        if distance or duration:
            res = []
            if distance: res.append(f"Mesafe: {distance}")
            if duration: res.append(f"Süre: {duration}")
            return " | ".join(res)
        
        return "Üzgünüm Hakan, bu iki nokta arası mesafe ve süre bilgisini kesin bir kaynaktan doğrulayamadım."
        
    except Exception as e:
        return f"Hata oluştu: {str(e)}"

if __name__ == "__main__":
    # Test
    print(get_distance_and_duration("Ankara", "İstanbul"))
