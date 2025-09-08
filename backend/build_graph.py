# backend/build_graph.py

import csv
import networkx as nx
import pickle
from itertools import combinations
from backend import config
from backend.graph_utils import load_data

def load_movies_and_stars(movies_file, stars_file):
    """Loads movies and stars data from their respective CSV files."""
    movies = {}
    stars = {}
    
    try:
        # Load movies
        with open(movies_file, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                movies[row['id']] = row['title']
        
        # Load stars relationships
        with open(stars_file, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                movie_id = row['movie_id']
                person_id = row['person_id']
                
                if movie_id not in stars:
                    stars[movie_id] = set()
                stars[movie_id].add(person_id)
                
    except FileNotFoundError as e:
        print(f"Error: Could not find required file: {e}")
        return {}, {}
    except Exception as e:
        print(f"Error loading movies and stars: {e}")
        return {}, {}
        
    return movies, stars

def build_graph(people, movies, stars):
    """Builds the networkx graph from the loaded data."""
    G = nx.Graph()
    
    # Add nodes with their names from the detailed dictionary
    for person_id, details in people.items():
        G.add_node(person_id, name=details['name'])
    
    print(f"Added {len(people)} nodes to graph")
    print("Building graph connections...")
    
    connection_count = 0
    for movie_id, actors in stars.items():
        movie_title = movies.get(movie_id, "Unknown Movie")
        
        # Filter out any actor IDs that might not be in our people list to prevent errors
        valid_actors = [actor_id for actor_id in actors if actor_id in people]
        
        # Create edges between all pairs of actors in this movie
        for p1, p2 in combinations(valid_actors, 2):
            if G.has_edge(p1, p2):
                # Add movie to existing edge
                existing_movies = G.edges[p1, p2].get('movies', [])
                if movie_title not in existing_movies:
                    existing_movies.append(movie_title)
                    G.edges[p1, p2]['movies'] = existing_movies
            else:
                # Create new edge
                G.add_edge(p1, p2, movies=[movie_title])
                connection_count += 1
    
    print(f"Created {connection_count} connections between actors")
    print(f"Graph has {G.number_of_nodes()} nodes and {G.number_of_edges()} edges")
    
    return G

def main():
    """Main function to build and save the graph."""
    print("Loading all data...")
    
    # Check if data files exist
    if not all([
        config.PEOPLE_FILE and os.path.exists(config.PEOPLE_FILE),
        config.MOVIES_FILE and os.path.exists(config.MOVIES_FILE),
        config.STARS_FILE and os.path.exists(config.STARS_FILE)
    ]):
        print("Error: Required data files not found. Please run scraper.py first.")
        print(f"Looking for:")
        print(f"  - {config.PEOPLE_FILE}")
        print(f"  - {config.MOVIES_FILE}") 
        print(f"  - {config.STARS_FILE}")
        return
    
    # Load data
    people_details, _ = load_data(config.PEOPLE_FILE)
    movies_data, stars_data = load_movies_and_stars(config.MOVIES_FILE, config.STARS_FILE)
    
    if not people_details or not movies_data or not stars_data:
        print("Error: Failed to load required data")
        return
    
    # Build graph
    graph = build_graph(people_details, movies_data, stars_data)
    
    # Save graph
    print(f"Saving graph to {config.GRAPH_PKL}...")
    try:
        with open(config.GRAPH_PKL, "wb") as f:
            pickle.dump(graph, f)
        print("✅ Graph building complete and saved successfully!")
    except Exception as e:
        print(f"Error saving graph: {e}")

if __name__ == "__main__":
    import os
    main()