# backend/graph_utils.py

import csv
import networkx as nx
from backend import config

def load_data(people_file):
    """
    Loads all person details (id, name, birth year) and creates two mappings:
    1. A dictionary of all person details mapped by ID.
    2. A dictionary mapping lowercase names to a set of person IDs for quick lookups.
    """
    people_details = {}  # Maps person_id to a dict of their details
    names = {}  # Maps lowercase name to a set of person_ids

    try:
        with open(people_file, encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                person_id = row["id"]
                
                # Store the full details for each person as a dictionary
                people_details[person_id] = {
                    "name": row["name"],
                    "birth": row["birth"]
                }

                # For the name mapping, handle multiple people with the same name
                lname = row["name"].lower()
                if lname not in names:
                    names[lname] = {person_id}
                else:
                    names[lname].add(person_id)
                    
    except FileNotFoundError:
        print(f"Error: Could not find file {people_file}")
        return {}, {}
    except Exception as e:
        print(f"Error loading data: {e}")
        return {}, {}

    return people_details, names

def find_path(graph, people_details, source_id, target_id):
    """
    Finds the shortest path between two person IDs using NetworkX.
    """
    try:
        path_nodes = nx.shortest_path(graph, source=source_id, target=target_id)
    except nx.NetworkXNoPath:
        return {"error": "No connection found", "degrees": float('inf'), "path": None}
    except nx.NodeNotFound:
        return {"error": "One or both actors not found in graph", "degrees": float('inf'), "path": None}

    degrees = len(path_nodes) - 1
    path_details = []

    for i in range(degrees):
        p1_id = path_nodes[i]
        p2_id = path_nodes[i+1]
        movies = graph.edges[p1_id, p2_id].get("movies", [])

        path_details.append({
            "person1": people_details[p1_id]['name'],
            "person2": people_details[p2_id]['name'],
            "movies": movies
        })

    return {"error": None, "degrees": degrees, "path": path_details}