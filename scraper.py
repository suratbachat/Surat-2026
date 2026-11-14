import os
import json
import time
import datetime
import requests
from bs4 import BeautifulSoup

API_KEY = os.environ.get("SCRAPER_API_KEY", "")

SEARCH_TOPICS = [
    {"query": "sugar", "cat": "Grocery", "kw": "sugar chini khand"},
    {"query": "atta", "cat": "Grocery", "kw": "atta flour gehu"},
    {"query": "sunflower oil", "cat": "Grocery", "kw": "oil tel fortune"},
    {"query": "milk", "cat": "Grocery", "kw": "milk doodh amul"},
    {"query": "bread", "cat": "Grocery", "kw": "bread pav"},
    {"query": "moong dal", "cat": "Grocery", "kw": "moong dal mung"},
    {"query": "tea", "cat": "Grocery", "kw": "tea chai patti"},
    {"query": "basmati rice", "cat": "Grocery", "kw": "rice chawal"},
    {"query": "biscuits", "cat": "Grocery", "kw": "biscuit cookies"},
    {"query": "detergent", "cat": "Grocery", "kw": "surf detergent soap"},
    {"query": "perfume", "cat": "Personal", "kw": "perfume deo bella vita"},
    {"query": "toothpaste", "cat": "Personal", "kw": "colgate toothpaste"},
    {"query": "notebook", "cat": "Stationery", "kw": "notebook copy book"},
    {"query": "gel pen", "cat": "Stationery", "kw": "pen gel trimax"},
    {"query": "earbuds", "cat": "Electronics", "kw": "earphones earbuds boat"}
]

def fetch_via_proxy(target_url):
    if not API_KEY:
        return None
    payload = {
        "api_key": API_KEY,
        "url": target_url,
        "country_code": "in",
        "render": "true"
    }
    try:
        res = requests.get("https://scraperapi.com", params=payload, timeout=45)
        if res.status_code == 200:
            return res.text
    except Exception:
        return None
    return None

def run_pipeline():
    try:
        with open("products.json", "r", encoding="utf-8") as f:
            existing_db = json.load(f)
    except Exception:
        existing_db = []

    now_str = datetime.datetime.now().strftime("%d %b, %I:%M %p")
    updated_items = []

    for topic in SEARCH_TOPICS[:5]:
        url = f"https://jiomart.com{topic['query']}"
        html = fetch_via_proxy(url)
        if html:
            soup = BeautifulSoup(html, "html.parser")
            titles = soup.select(".plp-card-details-name")[:4]
            prices = soup.select(".plp-card-details-price span")[:4]
            for t, p in zip(titles, prices):
                name = t.get_text(strip=True)
                raw_p = "".join(ch for ch in p.get_text() if ch.isdigit())
                if name and raw_p:
                    base = int(raw_p)
                    updated_items.append({
                        "n": name,
                        "k": f"{name.lower()} {topic['kw']}",
                        "c": topic["cat"],
                        "o": "LIVE DEAL" if base % 2 == 0 else "",
                        "nw": 1 if "new" in name.lower() else 0,
                        "d": max(10, base - 4),
                        "r": base,
                        "s": base - 2,
                        "w": max(10, base - 3),
                        "b": base + 5,
                        "z": base + 4,
                        "u": now_str
                    })
        time.sleep(2.5)

    seen_names = {item["n"].lower() for item in updated_items}
    for old in existing_db:
        old["u"] = now_str
        if old["n"].lower() not in seen_names:
            updated_items.append(old)

    with open("products.json", "w", encoding="utf-8") as f:
        json.dump(updated_items, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    run_pipeline()
