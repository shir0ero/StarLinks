import pickle
import sys
import networkx as nx

def main():
    if len(sys.argv) > 1:
        sys.exit("Usage: python degrees.py")

    print("Loading graph...")
    with open("graph.pkl", "rb") as f:
        G = pickle.load(f)
    print("Graph loaded.")

    name1 = input("Name: ").strip().lower()
    if name1 not in G:
        sys.exit(f"Person '{name1}' not found in graph.")

    name2 = input("Name: ").strip().lower()
    if name2 not in G:
        sys.exit(f"Person '{name2}' not found in graph.")

    try:
        path = nx.shortest_path(G, source=name1, target=name2)
    except nx.NetworkXNoPath:
        print("Not connected.")
        return

    degrees = len(path) - 1
    print(f"{degrees} degrees of separation.")
    for i in range(degrees):
        person1 = path[i]
        person2 = path[i + 1]
        movie = G[person1][person2]["movie"]
        print(f"{i + 1}: {person1.title()} and {person2.title()} starred in {movie}")

if __name__ == "__main__":
    main()
