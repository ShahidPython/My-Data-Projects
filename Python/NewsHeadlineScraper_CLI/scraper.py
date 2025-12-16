import requests
from bs4 import BeautifulSoup
import time
import json
import os
from config import TIMEOUT, DELAY, CACHE_EXPIRY

CACHE_FILE = "headlines_cache.json"

def load_cache():
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_cache(url, headlines):
    cache = load_cache()
    cache[url] = {
        "headlines": headlines,
        "timestamp": time.time()
    }
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)

def get_cached_headlines(url):
    cache = load_cache()
    if url in cache:
        if time.time() - cache[url]["timestamp"] < CACHE_EXPIRY:
            return cache[url]["headlines"]
    return None

def fetch_headlines(url):
    # Check cache first
    cached = get_cached_headlines(url)
    if cached:
        return cached

    # Safety delay
    time.sleep(DELAY)

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=TIMEOUT)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        headlines = []

        for tag in soup.find_all("span", class_="titleline"):
            if (link := tag.find("a")):
                headlines.append(link.get_text(strip=True))

        save_cache(url, headlines)
        return headlines

    except Exception as e:
        print(f"⚠️ Error: {e}")
        return []