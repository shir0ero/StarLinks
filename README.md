# StarLinks

StarLinks is a Python-based project that finds the shortest connection between any two actors in the film industry — inspired by the "Six Degrees of Separation" theory.

Using real-world movie cast data, it maps the relationships between actors based on the films they've starred in together and calculates the shortest path between them using graph traversal algorithms.

---

## Features

- Calculate degrees of separation between two actors
- Uses CSV datasets of movies, actors, and roles
- Efficient graph-based implementation (BFS)
- Modular codebase with clear utility functions
- Designed for future integration into a visual web interface

---

## Dataset Structure

This project uses a dataset consisting of:

- `people.csv` — Actor IDs and names
- `movies.csv` — Movie IDs and titles
- `stars.csv` — Links actors to the movies they’ve appeared in

> These are stored in the `small/` folder for a lightweight demo.

---

## Technologies Used

- Python 3
- CSV parsing
- Breadth-First Search (BFS) for shortest path
- Planned frontend: HTML/CSS/JS with a graph visualization library (e.g. D3.js or Vis.js)

---

## Planned Features

- 🌐 Web interface to input actor names
- 📈 Graphical visualization of connections
- 🧠 Search suggestions with fuzzy actor matching
- 🔍 Highlight shortest connection path with movie titles

---

## Running the Project

1. Clone the repo:
   ```bash
   git clone https://github.com/shir0ero/degrees.git
   cd degrees
