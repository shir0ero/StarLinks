import csv
import networkx as nx
import pickle
import sys

# Globals
people = {}  # person_id -> name
names = {}   # lowercase name -> set of person_ids

def load_data(directory):
    """
    Load people dictionary and build names mapping.
    """
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            person_id = row["id"]
            name = row["name"]
            people[person_id] = name
            lower_name = name.lower()
            if lower_name not in names:
                names[lower_name] = {person_id}
            else:
                names[lower_name].add(person_id)

def person_id_for_name(name):
    """
    Return person_id for a given name after resolving ambiguities.
    """
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    elif len(person_ids) > 1:
        print(f"Which '{name}'?")
        for pid in person_ids:
            print(f"ID: {pid}, Name: {people[pid]}")
        try:
            selected_id = input("Intended Person ID: ").strip()
            if selected_id in person_ids:
                return selected_id
        except Exception:
            pass
        return None
    else:
        return person_ids[0]

def main():
    directory = sys.argv[1] if len(sys.argv) > 1 else "large"

    print("Loading data...")
    load_data(directory)
    print("Data loaded.")

    print("Loading graph...")
    with open("graph.pkl", "rb") as f:
        graph = pickle.load(f)
    print("Graph loaded.")

    source_name = input("Name: ")
    source_id = person_id_for_name(source_name)
    if source_id is None:
        print(f"Person '{source_name}' not found.")
        return

    target_name = input("Name: ")
    target_id = person_id_for_name(target_name)
    if target_id is None:
        print(f"Person '{target_name}' not found.")
        return

    try:
        path = nx.shortest_path(graph, source=source_id, target=target_id)
    except nx.NetworkXNoPath:
        print("Not connected.")
        return

    degrees = len(path) - 1
    print(f"{degrees} degrees of separation.")
    for i in range(degrees):
        person1 = people[path[i]]
        person2 = people[path[i + 1]]
        # Edges store movie_id in attribute 'movie' (assumed)
        movie = graph.edges[path[i], path[i + 1]]['movie']
        print(f"{i + 1}: {person1} and {person2} starred in {movie}")

if __name__ == "__main__":
    main()
