import requests

def get_gold_price():
    url = "https://api.exchangerate-api.com/v4/latest/USD"
    response = requests.get(url)
    data = response.json()
    
    if 'rates' in data and 'XAU' in data['rates']:
        gold_price = data['rates']['XAU']
        return f"SONUÇ: {gold_price}"
    else:
        return "HATA: Altın fiyatı bulunamadı."

print(get_gold_price())