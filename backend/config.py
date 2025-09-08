# backend/config.py

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Base directory (parent of backend directory)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# --- Local Data Configuration ---
# Data files are now in the data/ directory
DATA_DIR = os.path.join(BASE_DIR, "data")
PEOPLE_FILE = os.path.join(DATA_DIR, "people.csv")
MOVIES_FILE = os.path.join(DATA_DIR, "movies.csv")
STARS_FILE = os.path.join(DATA_DIR, "stars.csv")
GRAPH_PKL = os.path.join(DATA_DIR, "graph.pkl")

# Create data directory if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)

# --- External API Configuration ---
# Get API key from environment variables (more secure)
TMDB_API_KEY = os.getenv('TMDB_API_KEY', "8de530608175c1e8c8f4d044b94b4187")

# Flask Configuration
FLASK_ENV = os.getenv('FLASK_ENV', 'development')
FLASK_DEBUG = os.getenv('FLASK_DEBUG', 'True').lower() == 'true'
FLASK_HOST = os.getenv('FLASK_HOST', 'localhost')
FLASK_PORT = int(os.getenv('FLASK_PORT', 5001))

# API Configuration
MAX_SEARCH_RESULTS = int(os.getenv('MAX_SEARCH_RESULTS', 10))
API_TIMEOUT = int(os.getenv('API_TIMEOUT', 30))
CORS_ORIGINS = os.getenv('CORS_ORIGINS', '*')

# Performance Settings
MAX_WORKERS = int(os.getenv('MAX_WORKERS', 20))
CACHE_TIMEOUT = int(os.getenv('CACHE_TIMEOUT', 3600))

# Print configuration for debugging (only in development)
if FLASK_DEBUG:
    print(f"Configuration loaded:")
    print(f"  Base directory: {BASE_DIR}")
    print(f"  Data directory: {DATA_DIR}")
    print(f"  TMDB API Key: {'✓ Set' if TMDB_API_KEY else '✗ Missing'}")
    print(f"  Flask port: {FLASK_PORT}")