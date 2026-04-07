import requests

def get_weather(city):
    try:
        res = requests.get(f"https://wttr.in/{city.strip()}?format=3&lang=tr", timeout=10)
        return res.text.strip() if res.status_code == 200 else f"{city} havası alınamadı."
    except: return "Hava durumu servisi kapalı."
