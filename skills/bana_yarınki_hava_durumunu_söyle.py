import requests
from bs4 import BeautifulSoup

def get_yesterday_weather():
    # Havadurumu için kullanacağımız API URL'i
    url = "https://www.hurriyetemlak.com/haber-detay/ist-anadolu-bogazici-istihdam-acikligi-ve-fiyatlarin-donusu-neler-konustu-672511"

    # Request gönder ve cevap al
    response = requests.get(url)

    # Cevapın HTML kodunu parse et
    soup = BeautifulSoup(response.content, 'html.parser')

    # Havadurumu için aradığımız metni bul
    weather_text = soup.find(text=lambda t: t.startswith("Hava Durumu")).strip()

    return weather_text

def main():
    yesterday_weather = get_yesterday_weather()
    print(f"SONUÇ: {yesterday_weather}")

if __name__ == "__main__":
    main()