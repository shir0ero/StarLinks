import networkx as nx

def load_data(directory="large"):
    import csv
    people = {}
    names = {}
    with open(f"{directory}/people.csv", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            person_id = row["id"]
            name = row["name"]
            people[person_id] = name
            lname = name.lower()
            if lname not in names:
                names[lname] = {person_id}
            else:
                names[lname].add(person_id)
    return people, names

def person_id_for_name(names, people, name):
    person_ids = list(names.get(name.lower(), set()))
    if len(person_ids) == 0:
        return None
    if len(person_ids) == 1:
        return person_ids[0]
    # If multiple, just return the first for now
    # You can extend this to handle ambiguity later
    return person_ids[0]

def find_degrees(graph, people, names, source_name, target_name):
    source_id = person_id_for_name(names, people, source_name)
    target_id = person_id_for_name(names, people, target_name)
    if source_id is None or target_id is None:
        return {"error": "Person not found", "degrees": None, "path": None}

    try:
        path = nx.shortest_path(graph, source=source_id, target=target_id)
    except nx.NetworkXNoPath:
        return {"error": "No connection found", "degrees": float('inf'), "path": None}

    degrees = len(path) - 1
    path_list = []
    for i in range(degrees):
        p1 = path[i]
        p2 = path[i+1]
        movies = graph.edges[p1, p2]["movies"]
        path_list.append({
            "person1": people[p1],
            "person2": people[p2],
            "movie": movies[0]  # Just first movie for simplicity
        })

    return {"error": None, "degrees": degrees, "path": path_list}
