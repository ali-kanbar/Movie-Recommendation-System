import os, asyncio, random, time, csv, sys
from typing import Dict, Any, Optional, Set, List
import aiohttp
import pandas as pd
from dotenv import load_dotenv

API_KEY = os.getenv("API_KEY")
OUT_CSV = "TMBD Movie Recommendation System Dataset.csv"
TARGET_ROWS = 10_000

OVERSAMPLE_FACTOR = 20.0 
DISCOVER_PAGES = 500 

if not API_KEY:
    print("Error: TMDB_API_KEY env var not set.", file=sys.stderr)
    sys.exit(1)

BASE = "https://api.themoviedb.org/3"

class RateLimiter:
    def __init__(self, rate: int, per: float):
        self.rate, self.per = rate, per
        self.tokens, self.updated = rate, time.monotonic()
        self.lock = asyncio.Lock()
    async def acquire(self):
        async with self.lock:
            now = time.monotonic()
            elapsed = now - self.updated
            self.tokens = min(self.rate, self.tokens + elapsed * (self.rate / self.per))
            self.updated = now
            if self.tokens < 1:
                await asyncio.sleep((1 - self.tokens) * (self.per / self.rate))
                self.tokens = 0
                self.updated = time.monotonic()
            else:
                self.tokens -= 1

limiter = RateLimiter(35, 10)

def parse_row(data: Dict[str, Any]) -> Dict[str, Any]:
    genres = ", ".join([g["name"] for g in data.get("genres", []) if g.get("name")])
    companies = ", ".join([c["name"] for c in data.get("production_companies", []) if c.get("name")])
    
    keywords_data = data.get("keywords", {}).get("keywords", [])
    keywords = ", ".join([k["name"] for k in keywords_data])
    
    credits = data.get("credits", {})
    crew = credits.get("crew", [])
    cast = credits.get("cast", [])
    
    director = next((c["name"] for c in crew if c.get("job") == "Director"), None)
    top_cast = [c["name"] for c in sorted(cast, key=lambda x: x.get("order", 999))[:3]]
    actor1, actor2, actor3 = (top_cast + [None, None, None])[:3]
    
    return {
        "id": data.get("id"), "title": data.get("title"), "release_date": data.get("release_date"),
        "overview": data.get("overview"),
        "keywords": keywords,
        "original_language": data.get("original_language"), "runtime": data.get("runtime"),
        "vote_average": data.get("vote_average"), "vote_count": data.get("vote_count"),
        "popularity": data.get("popularity"), "genres": genres, "director": director,
        "actor1": actor1, "actor2": actor2, "actor3": actor3, "budget": data.get("budget"),
        "revenue": data.get("revenue"), "imdb_id": data.get("imdb_id"), "production_companies": companies,
    }

async def get_json(session, url, params, retries=4):
    for attempt in range(retries):
        await limiter.acquire()
        try:
            async with session.get(url, params=params, timeout=30) as r:
                if r.status == 429: await asyncio.sleep(2); continue
                r.raise_for_status()
                return await r.json()
        except Exception:
            if attempt == retries - 1: return None
            await asyncio.sleep(1.5 * (attempt + 1))
    return None

async def discover_ids(session, target: int) -> List[int]:
    need = int(target * OVERSAMPLE_FACTOR) # e.g., 200,000
    ids: Set[int] = set()
    
    current_year = 2024 
    search_years = list(range(1960, current_year + 1))
    random.shuffle(search_years)
    
    print(f"Searching for {need} movie IDs across {len(search_years)} years...")
    
    for year in search_years:
        for page in range(1, DISCOVER_PAGES + 1):
            if len(ids) >= need: break 
            
            params = {
                "api_key": API_KEY, "language": "en-US", "include_adult": "false",
                "sort_by": "popularity.desc",
                "vote_count.gte": 100, 
                "primary_release_year": year, 
                "page": page,
            }
            
            data = await get_json(session, f"{BASE}/discover/movie", params)
            if not data or not data.get("results"):
                break 
            
            for it in data["results"]:
                if "id" in it: ids.add(it["id"])
            
            if len(ids) % 5000 == 0 and len(ids) > 0:
                print(f"  Found {len(ids)}/{need} unique IDs...")

        if len(ids) >= need: break 

    print(f"Discovery complete. Found {len(ids)} total IDs.")
    return list(ids)

async def fetch_movie(session, mid: int) -> Optional[Dict[str, Any]]:
    params = {"api_key": API_KEY, "language": "en-US", "append_to_response": "credits,keywords"}
    data = await get_json(session, f"{BASE}/movie/{mid}", params)
    if not data: return None
    return parse_row(data)

async def main():
    async with aiohttp.ClientSession() as session:
        print("Discovering IDs…")
        ids = await discover_ids(session, TARGET_ROWS)
        random.shuffle(ids)

        rows = []
        print(f"\nFetching details for {len(ids)} movies...")
        for i, mid in enumerate(ids, 1):
            if len(rows) >= TARGET_ROWS: break
            
            row = await fetch_movie(session, mid)
            
            if (row and 
                row.get("genres") and 
                row.get("actor1") and 
                row.get("runtime", 0) > 60 and
                row.get("budget", 0) > 0 and  
                row.get("revenue", 0) > 0): 
                rows.append(row)

            if i % 500 == 0:
                print(f"  {i}/{len(ids)} IDs checked, {len(rows)}/{TARGET_ROWS} complete movies saved…")

        df = pd.DataFrame(rows).drop_duplicates("id").reset_index(drop=True)
        if len(df) > TARGET_ROWS:
            df = df.iloc[:TARGET_ROWS]
        
        df.to_csv(OUT_CSV, index=False, quoting=csv.QUOTE_MINIMAL)
        print(f"\nDone: {len(df)} rows saved to {OUT_CSV}")

if __name__ == "__main__":
    asyncio.run(main())