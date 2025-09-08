# backend/scraper.py

import csv
import requests
import time
import os
import config
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- Configuration ---
# How many pages of popular movies to scrape from TMDb
PAGES_TO_SCRAPE = 500
# Number of concurrent workers for fetching data
MAX_WORKERS = 20

def api_request(url, params):
    """Makes a single, robust request to the TMDb API."""
    try:
        response = requests.get(url, params=params, timeout=15)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"API request failed: {e}")
        return None

def fetch_movie_credits(movie_info):
    """Worker function to fetch cast for a single movie."""
    movie_id, _, _ = movie_info
    params = {"api_key": config.TMDB_API_KEY}
    credits = api_request(f"https://api.themoviedb.org/3/movie/{movie_id}/credits", params)
    
    if credits and credits.get("cast"):
        return movie_id, credits["cast"]
    return movie_id, []

def fetch_person_details(person_id):
    """Worker function to fetch details for a single person."""
    params = {"api_key": config.TMDB_API_KEY}
    details = api_request(f"https://api.themoviedb.org/3/person/{person_id}", params)
    
    if details and details.get("birthday"):
        return {
            "id": details["id"],
            "name": details["name"],
            "birth": details["birthday"][:4]
        }
    return None

def scrape_data():
    """Scrapes movie and actor data from TMDb concurrently."""
    print("🎬 Starting TMDb data scraping process...")
    
    if not config.TMDB_API_KEY:
        print("❌ Error: TMDB_API_KEY not found. Please set it in your .env file.")
        return
    
    # --- Step 1: Fetch all popular movies ---
    movie_list = []
    print(f"📽️  Fetching {PAGES_TO_SCRAPE} pages of popular movies...")
    
    for page in tqdm(range(1, PAGES_TO_SCRAPE + 1), desc="Scraping Movie Pages"):
        params = {"api_key": config.TMDB_API_KEY, "page": page}
        data = api_request("https://api.themoviedb.org/3/movie/popular", params)
        
        if data and data.get("results"):
            for movie in data["results"]:
                if movie.get("release_date"):
                    movie_list.append((movie["id"], movie["title"], movie["release_date"][:4]))
        
        time.sleep(0.05)  # Rate limiting
    
    if not movie_list:
        print("❌ Scraping failed: No movie data collected. Check your API key.")
        return
    
    print(f"✅ Found {len(movie_list)} movies")
    
    # --- Step 2: Fetch movie credits concurrently ---
    print(f"🎭 Fetching cast details for {len(movie_list)} movies...")
    movie_credits_map = {}
    unique_person_ids = set()
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_movie = {executor.submit(fetch_movie_credits, movie): movie for movie in movie_list}
        
        for future in tqdm(as_completed(future_to_movie), total=len(movie_list), desc="Fetching Casts"):
            movie_id, cast = future.result()
            # Take top 15 cast members per movie
            top_cast_ids = [actor["id"] for actor in cast[:15]]
            movie_credits_map[movie_id] = top_cast_ids
            unique_person_ids.update(top_cast_ids)
    
    print(f"✅ Found {len(unique_person_ids)} unique actors")
    
    # --- Step 3: Fetch person details concurrently ---
    print(f"👥 Fetching person details for {len(unique_person_ids)} unique actors...")
    people_map = {}
    
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_person = {executor.submit(fetch_person_details, pid): pid for pid in unique_person_ids}
        
        for future in tqdm(as_completed(future_to_person), total=len(unique_person_ids), desc="Fetching People"):
            person_data = future.result()
            if person_data:
                people_map[person_data["id"]] = person_data
    
    print(f"✅ Got details for {len(people_map)} actors")
    
    # --- Step 4: Assemble final datasets and write to CSV ---
    print("💾 Assembling and writing data to CSV files...")
    
    final_movies = sorted(list(set(movie_list)))
    final_people = sorted(list(people_map.values()), key=lambda p: p["id"])
    
    # Create the stars relationship table
    stars = []
    for movie_id, cast_ids in movie_credits_map.items():
        for person_id in cast_ids:
            # Only add the relationship if we have the person's details
            if person_id in people_map:
                stars.append((person_id, movie_id))
    
    # Write CSV files
    try:
        # Movies
        with open(config.MOVIES_FILE, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["id", "title", "year"])
            writer.writerows(final_movies)
        print(f"✅ Wrote {len(final_movies)} movies to {config.MOVIES_FILE}")
        
        # People
        with open(config.PEOPLE_FILE, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["id", "name", "birth"])
            writer.writeheader()
            writer.writerows(final_people)
        print(f"✅ Wrote {len(final_people)} people to {config.PEOPLE_FILE}")
        
        # Stars relationships
        with open(config.STARS_FILE, "w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["person_id", "movie_id"])
            writer.writerows(sorted(stars))
        print(f"✅ Wrote {len(stars)} star connections to {config.STARS_FILE}")
        
        print("\n🎉 All files created successfully!")
        print("📊 Next steps:")
        print("  1. Run: python backend/build_graph.py")
        print("  2. Start API: python backend/api.py")
        
    except Exception as e:
        print(f"❌ Error writing files: {e}")

def main():
    """Main function to run the scraper."""
    print("StarLinks Data Scraper")
    print("=" * 30)
    
    # Check if data directory exists
    os.makedirs(config.DATA_DIR, exist_ok=True)
    
    scrape_data()

if __name__ == "__main__":
    # Suppress SSL warnings for cleaner output
    requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
    main()