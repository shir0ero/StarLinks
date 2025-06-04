# build_graph.py
import csv
import networkx as nx
import pickle

def load_people(filename):
    people = {}
    with open(filename, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            people[row['id']] = row['name']
    return people

def load_movies(filename):
    movies = {}
    with open(filename, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movies[row['id']] = row['title']
    return movies

def load_stars(filename):
    stars = {}
    with open(filename, encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            movie_id = row['movie_id']
            person_id = row['person_id']
            if movie_id not in stars:
                stars[movie_id] = set()
            stars[movie_id].add(person_id)
    return stars

def build_graph(people_file, movies_file, stars_file):
    people = load_people(people_file)
    movies = load_movies(movies_file)
    stars = load_stars(stars_file)

    G = nx.Graph()

    for person_id, name in people.items():
        G.add_node(person_id, name=name)

    for movie_id, actors in stars.items():
        movie_title = movies.get(movie_id, "Unknown")
        actors = list(actors)
        for i in range(len(actors)):
            for j in range(i + 1, len(actors)):
                if G.has_edge(actors[i], actors[j]):
                    existing = G.edges[actors[i], actors[j]].get('movies', [])
                    if movie_title not in existing:
                        existing.append(movie_title)
                    G.edges[actors[i], actors[j]]['movies'] = existing
                else:
                    G.add_edge(actors[i], actors[j], movies=[movie_title])

    return G, people

if __name__ == "__main__":
    G, people = build_graph("large/people.csv", "large/movies.csv", "large/stars.csv")
    with open("graph.pkl", "wb") as f:
        pickle.dump(G, f)
    with open("people.pkl", "wb") as f:
        pickle.dump(people, f)
    print("Graph and people data saved to graph.pkl and people.pkl")
