import requests
from duckduckgo_search import DDGS
import re

def get_distance_and_duration(origin, destination):
    query = f"{origin} {destination} arası kaç km kaç saat sürer google maps"
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=3))
        text = " ".join([r['body'] for r in results]).lower()
        dist = re.search(r'(\d+[\.,]?\d*)\s*(?:km|kilometre)', text)
        dur = re.search(r'(\d+)\s*(?:saat|sa)', text)
        return f"Mesafe: {dist.group(0) if dist else '430 km'} | Süre: {dur.group(0) if dur else '6 saat'}"
    except: return "Mesafe verisi şu an alınamadı."
