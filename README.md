# 🌟 StarLinks: Actor Degrees of Separation

Inspired by the "Six Degrees of Kevin Bacon" game, **StarLinks** is a Python project that calculates the *degrees of separation* between any two actors.  
It builds a graph of actors and their co-starring relationships, then finds the shortest path connecting them.  

The project includes both a **command-line tool** and a **RESTful API**, making it easy to explore or integrate.

---

## ✨ Features

- **Graph-Based Analysis** – Uses [NetworkX](https://networkx.org/) to model actor relationships as a graph.  
- **Degrees of Separation** – Efficiently computes the shortest path between two actors.  
- **Detailed Path Output** – Returns not only the number of degrees but also the movies linking each pair.  
- **Command-Line Interface** – A simple, interactive CLI (`degrees.py`) for quick lookups.  
- **RESTful API** – A Flask-based API (`api.py`) to integrate with other apps or services.  
- **Fast Startup** – Graphs are pre-built and serialized with `pickle` for quick loading.  

---

## 🚀 Getting Started

### Prerequisites

- Python **3.6+**
- Required libraries:
  ```bash
  pip install Flask networkx


### 📦 Data Files
The project relies on three CSV files to build the actor graph. Place these files in the same directory or update paths in `build_graph.py` as needed:
- `people.csv` — Actor IDs and names (e.g. `person_id,name,birth`)  
- `movies.csv` — Movie IDs and titles (e.g. `movie_id,title,year`)  
- `stars.csv` — Links actors to movies (e.g. `movie_id,person_id`)  

You can use the included datasets (`large/`, `small/`) or build your own dataset (for example from TMDB).

---

### 🔨 Build the Graph
Before running the application, build and serialize the graph:

This will create:
- `graph.pkl` — Serialized actor graph (NetworkX graph)  
- `people.pkl` — Serialized people dictionary (ID → name data)  

---

## 🤝 Contribution
Contributions are welcome!  
- 🐛 Found a bug? Open an issue.  
- 💡 Have a feature idea? Start a discussion or open an issue.  
- 🔧 Want to contribute code? Submit a pull request.  
