import requests
from bs4 import BeautifulSoup

def bitcoin_fiyatini_al():
    url = "https://www.google.com/search?q=bitcoin+fiyatı"
    response = requests.get(url)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        fiyat_bulunan_satir = None
        for satir in soup.find_all('div', class_='BNeawe'):
            if "Bitcoin Fiyatı" in satir.text:
                fiyat_bulunan_satir = satir
                
        if fiyat_bulunan_satir is not None:
            fiyat = fiyat_bulunan_satir.text.split()[-1]
            return f'SONUÇ: {fiyat}'
        else:
            return "SONUÇ: Fiyat bulunamadı."
    else:
        return "SONUÇ: İnternet bağlantısı kurulamadı."

print(bitcoin_fiyatini_al())