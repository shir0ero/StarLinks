# backend/degrees.py

import pickle
import sys
import os
import config
from graph_utils import load_data, find_path

def get_person_id(people, names, prompt):
    """
    Interactively prompts the user for a name and handles ambiguity
    by letting the user choose from a list of matches.
    """
    while True:
        name = input(prompt).strip()
        if not name:
            print("Please enter a name.")
            continue
        
        # Search for exact matches and partial matches
        person_ids = set()
        
        # Exact match
        exact_matches = names.get(name.lower(), set())
        person_ids.update(exact_matches)
        
        # Partial matches if no exact match
        if not person_ids:
            for stored_name, pids in names.items():
                if name.lower() in stored_name or stored_name in name.lower():
                    person_ids.update(pids)
        
        person_ids = list(person_ids)
        
        if not person_ids:
            print(f"No actor found with the name '{name}'. Please try again.")
            continue
        
        if len(person_ids) == 1:
            return person_ids[0]
        
        # If ambiguous, present options
        print(f"Multiple actors found for '{name}':")
        for i, person_id in enumerate(person_ids[:10]):  # Limit to 10 results
            person_info = people[person_id]
            print(f" {i + 1}: {person_info['name']} (born {person_info['birth']})")
        
        while True:
            try:
                choice = input("Please select one by number: ").strip()
                if not choice:
                    continue
                    
                choice_index = int(choice) - 1
                if 0 <= choice_index < len(person_ids):
                    return person_ids[choice_index]
                else:
                    print("Invalid choice. Please pick a number from the list.")
            except ValueError:
                print("Invalid input. Please enter a number.")

def display_path_result(result):
    """Display the path result in a nice format."""
    if result["error"]:
        print(f"\n❌ Error: {result['error']}")
        return
    
    print(f"\n🎯 Found! {result['degrees']} degrees of separation")
    print("=" * 50)
    
    for i, step in enumerate(result["path"], 1):
        movies_str = ", ".join(step['movies'][:3])  # Show first 3 movies
        if len(step['movies']) > 3:
            movies_str += f" (and {len(step['movies']) - 3} more)"
        
        print(f"{i}. {step['person1']} → {step['person2']}")
        print(f"   Movies: {movies_str}")
    
    print("=" * 50)

def main():
    """Main function to run the command-line interface."""
    print("🎬 StarLinks - Actor Connection Finder (CLI)")
    print("=" * 50)
    
    # Check if data files exist
    if not os.path.exists(config.PEOPLE_FILE):
        print(f"❌ Error: {config.PEOPLE_FILE} not found.")
        print("Please run the scraper first: python backend/scraper.py")
        return
    
    if not os.path.exists(config.GRAPH_PKL):
        print(f"❌ Error: {config.GRAPH_PKL} not found.")
        print("Please build the graph first: python backend/build_graph.py")
        return
    
    print("Loading data...")
    
    try:
        # Load people data
        people, names = load_data(config.PEOPLE_FILE)
        print(f"✅ Loaded {len(people)} actors")
        
        # Load graph
        with open(config.GRAPH_PKL, "rb") as f:
            graph = pickle.load(f)
        print(f"✅ Loaded graph with {graph.number_of_nodes()} nodes and {graph.number_of_edges()} edges")
        
    except Exception as e:
        print(f"❌ Error loading data: {e}")
        return
    
    print("\n🚀 Ready to find connections! (Press Ctrl+C to exit)")
    print("Try actors like: Tom Hanks, Natalie Portman, Morgan Freeman, etc.")
    print()
    
    try:
        while True:
            print("-" * 30)
            source_id = get_person_id(people, names, "🎭 Enter first actor's name: ")
            target_id = get_person_id(people, names, "🎭 Enter second actor's name: ")
            
            if source_id == target_id:
                print("\n😄 Source and target are the same person (0 degrees)!")
                continue
            
            print(f"\n🔍 Finding path between {people[source_id]['name']} and {people[target_id]['name']}...")
            
            result = find_path(graph, people, source_id, target_id)
            display_path_result(result)
            
            # Ask if user wants to continue
            while True:
                continue_choice = input("\n🔄 Find another connection? (y/n): ").lower().strip()
                if continue_choice in ['y', 'yes', '']:
                    break
                elif continue_choice in ['n', 'no']:
                    print("👋 Thanks for using StarLinks!")
                    return
                else:
                    print("Please enter 'y' or 'n'")
    
    except (KeyboardInterrupt, EOFError):
        print("\n\n👋 Exiting StarLinks. Goodbye!")
        sys.exit(0)

if __name__ == "__main__":
    main()