import sys
import pickle
from graph_utils import load_data, find_degrees

def main():
    directory = sys.argv[1] if len(sys.argv) > 1 else "large"
    print("Loading data...")
    people, names = load_data(directory)
    print("Data loaded.")

    print("Loading graph...")
    with open("graph.pkl", "rb") as f:
        graph = pickle.load(f)
    print("Graph loaded.")

    source_name = input("Name: ")
    target_name = input("Name: ")

    result = find_degrees(graph, people, names, source_name, target_name)
    if result["error"]:
        print(result["error"])
        return

    print(f"{result['degrees']} degrees of separation.")
    for i, step in enumerate(result["path"], 1):
        print(f"{i}: {step['person1']} and {step['person2']} starred in {step['movie']}")

if __name__ == "__main__":
    main()
