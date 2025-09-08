# Enhanced API with Social Links Support

import pickle
import requests
from flask import Flask, request, jsonify
from flask_cors import CORS
from backend import config
from backend import graph_utils
from graph_utils import load_data, find_path
import networkx as nx
from itertools import combinations
from datetime import datetime

# Initialize Flask app and enable CORS
app = Flask(__name__)
CORS(app)

# --- Load data once at startup ---
print("Loading data for API...")
PEOPLE_DETAILS, NAMES = load_data(config.PEOPLE_FILE)
print("Loading graph for API...")
with open(config.GRAPH_PKL, "rb") as f:
    GRAPH = pickle.load(f)

print("📋 Available endpoints:")
print("  GET  /                    - Health check")
print("  GET  /find_actors?name=X  - Search actors")
print("  POST /path_by_id          - Find connection path")
print("  POST /network             - Generate network graph")
print("  GET  /actor_profile/<id>  - Actor details")
print("  GET  /actor_social/<id>   - Social media links")
print("🌐 Frontend: Open frontend/index.html in your browser")
print("⏹️  Press Ctrl+C to stop the server")
print("Server is ready.")

def get_tmdb_details_by_id(person_id):
    """Fetches detailed actor information from TMDb using the person's ID."""
    if not config.TMDB_API_KEY:
        return None
    try:
        url = f"https://api.themoviedb.org/3/person/{person_id}"
        params = {"api_key": config.TMDB_API_KEY, "append_to_response": "movie_credits,external_ids"}
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.RequestException:
        return None

@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint."""
    return jsonify({
        "status": "healthy",
        "message": "StarLinks API is running",
        "actors_count": len(PEOPLE_DETAILS),
        "graph_nodes": GRAPH.number_of_nodes(),
        "graph_edges": GRAPH.number_of_edges()
    })

@app.route("/find_actors", methods=["GET"])
def find_actors_by_name():
    """Finds actors by name from local data."""
    name = request.args.get("name", "").lower().strip()
    if not name:
        return jsonify({"error": "Actor name query is required."}), 400

    matching_ids = list(NAMES.get(name, []))
    if not matching_ids:
        # Fuzzy search fallback
        fuzzy_matches = []
        for stored_name, ids in NAMES.items():
            if name in stored_name or stored_name in name:
                fuzzy_matches.extend(ids)
        
        if fuzzy_matches:
            matching_ids = list(set(fuzzy_matches))[:10]
        else:
            return jsonify([])

    results = [{"id": pid, "name": PEOPLE_DETAILS[pid]['name'], "birth": PEOPLE_DETAILS[pid]['birth']} 
               for pid in matching_ids]
    return jsonify(results[:10])

@app.route("/path_by_id", methods=["POST"])
def path_by_id():
    """Finds the shortest path between two specific actor IDs."""
    data = request.json
    source_id, target_id = data.get("source_id"), data.get("target_id")
    if not source_id or not target_id:
        return jsonify({"error": "Source and target IDs are required."}), 400

    if source_id == target_id:
        return jsonify({"degrees": 0, "path": []})

    try:
        path_nodes = nx.shortest_path(GRAPH, source=source_id, target=target_id)
    except nx.NetworkXNoPath:
        return jsonify({"error": "No connection found", "degrees": float('inf'), "path": None})

    degrees = len(path_nodes) - 1
    path_details = []

    for i in range(degrees):
        p1_id = path_nodes[i]
        p2_id = path_nodes[i+1]
        movies = GRAPH.edges[p1_id, p2_id].get("movies", [])
        path_details.append({
            "person1_id": p1_id,
            "person1": PEOPLE_DETAILS[p1_id]['name'],
            "person2_id": p2_id,
            "person2": PEOPLE_DETAILS[p2_id]['name'],
            "movies": movies
        })

    result = {"error": None, "degrees": degrees, "path": path_details}
    return jsonify(result)

@app.route("/network", methods=["POST"])
def get_network_graph():
    """Generates a subgraph connecting a list of specified actor IDs."""
    data = request.json
    actor_ids = list(set(data.get("actor_ids", [])))
    if len(actor_ids) < 2:
        return jsonify({"error": "Please provide at least two actors."}), 400

    all_path_nodes = set(actor_ids)
    for p1, p2 in combinations(actor_ids, 2):
        try:
            path = nx.shortest_path(GRAPH, source=p1, target=p2)
            all_path_nodes.update(path)
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            continue

    subgraph = GRAPH.subgraph(all_path_nodes)
    nodes = [{"id": nid, 
              "label": PEOPLE_DETAILS[nid]["name"], 
              "color": "#667eea" if nid in actor_ids else "#C19A6B", 
              "size": 25 if nid in actor_ids else 15} 
             for nid in subgraph.nodes()]
    
    edges = [{"from": p1, "to": p2, "title": ", ".join(edata.get("movies", []))} 
             for p1, p2, edata in subgraph.edges(data=True)]

    return jsonify({"nodes": nodes, "edges": edges})

@app.route("/actor_profile/<person_id>", methods=["GET"])
def get_actor_profile(person_id):
    """Fetches and processes detailed information for a single actor."""
    profile_data = get_tmdb_details_by_id(person_id)
    if not profile_data:
        return jsonify({"error": "Failed to fetch details from TMDb."}), 500

    credits = profile_data.get('movie_credits', {}).get('cast', [])
    valid_films = sorted([f for f in credits if f.get('release_date') and f.get('vote_average', 0) > 0], 
                        key=lambda x: x.get('release_date', ''))

    movies_per_year = {}
    for film in valid_films:
        try:
            year = datetime.strptime(film['release_date'], '%Y-%m-%d').year
            movies_per_year[year] = movies_per_year.get(year, 0) + 1
        except (ValueError, TypeError):
            continue

    sorted_years = sorted(movies_per_year.keys()) if movies_per_year else []

    response = {
        "profile": {
            "name": profile_data.get('name'),
            "biography": profile_data.get('biography'),
            "birthday": profile_data.get('birthday'),
            "deathday": profile_data.get('deathday'),
            "place_of_birth": profile_data.get('place_of_birth'),
            "profile_path": profile_data.get('profile_path')
        },
        "charts": {
            "ratings_over_time": {
                "labels": [f.get('title', 'Unknown') for f in valid_films],
                "data": [f.get('vote_average', 0) for f in valid_films]
            },
            "movies_per_year": {
                "labels": [str(y) for y in sorted_years],
                "data": [movies_per_year[y] for y in sorted_years]
            }
        } if valid_films else None,
        "total_movies": len(valid_films),
        "career_span": f"{sorted_years[0]} - {sorted_years[-1]}" if len(sorted_years) > 1 else str(sorted_years[0]) if sorted_years else "Unknown"
    }

    return jsonify(response)

@app.route("/actor_social/<person_id>", methods=["GET"])
def get_actor_social(person_id):
    """Fetches social media links for an actor."""
    # Get basic profile data first
    profile_data = get_tmdb_details_by_id(person_id)
    if not profile_data:
        return jsonify({"error": "Failed to fetch actor details from TMDb."}), 500
    
    actor_name = profile_data.get('name', '')
    external_ids = profile_data.get('external_ids', {})
    
    # Build social links from available data
    social_links = []
    
    # IMDb (always available from TMDb)
    if external_ids.get('imdb_id'):
        social_links.append({
            "platform": "IMDb",
            "icon": "fab fa-imdb",
            "username": actor_name,
            "url": f"https://imdb.com/name/{external_ids['imdb_id']}",
            "verified": True
        })
    
    # Instagram
    if external_ids.get('instagram_id'):
        social_links.append({
            "platform": "Instagram",
            "icon": "fab fa-instagram",
            "username": f"@{external_ids['instagram_id']}",
            "url": f"https://instagram.com/{external_ids['instagram_id']}",
            "verified": True
        })
    
    # Twitter/X
    if external_ids.get('twitter_id'):
        social_links.append({
            "platform": "Twitter",
            "icon": "fab fa-twitter",
            "username": f"@{external_ids['twitter_id']}",
            "url": f"https://twitter.com/{external_ids['twitter_id']}",
            "verified": True
        })
    
    # Facebook
    if external_ids.get('facebook_id'):
        social_links.append({
            "platform": "Facebook",
            "icon": "fab fa-facebook",
            "username": actor_name,
            "url": f"https://facebook.com/{external_ids['facebook_id']}",
            "verified": True
        })
    
    # TikTok
    if external_ids.get('tiktok_id'):
        social_links.append({
            "platform": "TikTok",
            "icon": "fab fa-tiktok",
            "username": f"@{external_ids['tiktok_id']}",
            "url": f"https://tiktok.com/@{external_ids['tiktok_id']}",
            "verified": True
        })
    
    # YouTube
    if external_ids.get('youtube_id'):
        social_links.append({
            "platform": "YouTube",
            "icon": "fab fa-youtube",
            "username": actor_name,
            "url": f"https://youtube.com/{external_ids['youtube_id']}",
            "verified": True
        })
    
    # Wikipedia (constructed from name)
    wikipedia_name = actor_name.replace(' ', '_')
    social_links.append({
        "platform": "Wikipedia",
        "icon": "fab fa-wikipedia-w",
        "username": actor_name,
        "url": f"https://en.wikipedia.org/wiki/{wikipedia_name}",
        "verified": False
    })
    
    # TMDb profile
    social_links.append({
        "platform": "The Movie DB",
        "icon": "fas fa-film",
        "username": actor_name,
        "url": f"https://themoviedb.org/person/{person_id}",
        "verified": True
    })
    
    # If no social links found, add some mock/potential links
    if len(social_links) <= 2:  # Only Wikipedia and TMDb
        name_handle = actor_name.lower().replace(' ', '').replace('.', '')
        
        mock_links = [
            {
                "platform": "Instagram",
                "icon": "fab fa-instagram",
                "username": f"@{name_handle}",
                "url": f"https://instagram.com/{name_handle}",
                "verified": False,
                "note": "Potential account - not verified"
            },
            {
                "platform": "Twitter",
                "icon": "fab fa-twitter", 
                "username": f"@{name_handle}",
                "url": f"https://twitter.com/{name_handle}",
                "verified": False,
                "note": "Potential account - not verified"
            }
        ]
        social_links.extend(mock_links)
    
    return jsonify({
        "actor_name": actor_name,
        "links": social_links,
        "total_links": len(social_links),
        "verified_links": len([link for link in social_links if link.get('verified', False)])
    })

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5001)