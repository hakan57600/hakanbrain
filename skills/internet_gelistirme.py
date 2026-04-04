import requests
from bs4 import BeautifulSoup
import urllib.parse

def internetten_arastir(sorgu, sonuc_sayisi=3):
    """
    Hakan Bey için her cihazda çalışacak (Evrensel) internet araştırma yeteneği.
    Sadece standart kütüphaneleri kullanarak DuckDuckGo Lite üzerinden veri çeker.
    """
    try:
        # Teknik arama terimlerini optimize et
        sorgu_encoded = urllib.parse.quote(f"{sorgu} technical documentation")
        # DuckDuckGo Lite (HTML) arayüzü - Bot engellerine en dirençli yoldur.
        url = f"https://lite.duckduckgo.com/lite/?q={sorgu_encoded}"
        
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7"
        }
        
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code != 200:
            return f"⚠️ İnternet erişim reddedildi (Hata: {response.status_code}), Hakan Bey."
            
        soup = BeautifulSoup(response.text, "html.parser")
        
        # DDG Lite sonuçlarını ayıkla (Tablo yapısı kullanır)
        sonuclar = []
        links = soup.find_all('a', class_='result-link')
        snippets = soup.find_all('td', class_='result-snippet')
        
        for i in range(min(len(links), sonuc_sayisi)):
            title = links[i].text.strip()
            link = links[i]['href']
            # Link temizleme (DDG yönlendirmelerini ayıkla)
            if "uddg=" in link:
                link = urllib.parse.unquote(link.split("uddg=")[1].split("&")[0])
            
            snippet = snippets[i].text.strip() if i < len(snippets) else "Özet bulunamadı."
            
            sonuclar.append({
                "baslik": title,
                "link": link,
                "ozet": snippet
            })
                
        if not sonuclar:
            return "İnternette bu konu hakkında evrensel bir döküman bulunamadı, Hakan Bey."
            
        # Teknik Rapor Hazırla
        rapor = f"🌍 [EVRENSEL TEKNİK RAPOR] - Sorgu: '{sorgu}'\n"
        for i, s in enumerate(sonuclar, 1):
            rapor += f"\n[{i}] {s['baslik']}\n"
            rapor += f"🔗 Kaynak: {s['link']}\n"
            rapor += f"📝 Analiz: {s['ozet'][:250]}...\n"
            
        return rapor
        
    except Exception as e:
        return f"⚠️ Evrensel araştırma sırasında bir aksaklık oluştu: {str(e)}, Hakan Bey."

if __name__ == "__main__":
    # Bağımsız Test (3. Aşama - Evrensel Yöntem)
    print("\n🌍 [İNTERNETTEN GELİŞTİRME - EVRENSEL TEST MODU] 🌍")
    print(internetten_arastir("Linux sistem yönetimi teknik döküman"))
