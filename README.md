# Smart Uber Ride Matching System

A Python simulation of an Uber-like ride matching system using AI and algorithmic techniques.

---

## Features
- Driver-passenger matching
- BFS shortest path finding
- Dynamic Programming optimization
- Greedy driver selection
- Animated driver movement
- Cost and time calculation
- Obstacle-based city grid
- Multiple ride requests support

---

## Algorithms Used

### BFS (Breadth First Search)
Used to find the shortest path between:
- Driver → Pickup
- Pickup → Destination

### Greedy Algorithm
Selects the nearest available driver.

### Dynamic Programming (DP)
Optimizes assignments when multiple ride requests exist.

### Divide and Conquer
Used for efficient path-related operations and system optimization.

---

## Project Structure

main.py
-> Main game and user interface

algorithms.py
-> BFS, DP, Greedy algorithms

models.py
-> Driver, Passenger, Request classes

Grid.py
-> Grid management and visualization

---

## How to Run

```bash
python main.py
