# core.py
# Core system logic: grid, BFS, cost calculation, and the main engine class

from collections import deque
import math



DIRECTIONS = [(0, 1), (0, -1), (1, 0), (-1, 0)]

def bfs(grid, N, M, start_r, start_c, end_r, end_c):
    """
    BFS shortest path on an N×M grid, avoiding 'X' obstacle cells.
    """
    if (start_r, start_c) == (end_r, end_c):
        return 0, [(start_r, start_c)]

    parent = {(start_r, start_c): None}
    queue = deque([(start_r, start_c, 0)])

    while queue:
        r, c, dist = queue.popleft()
        for dr, dc in DIRECTIONS:
            nr, nc = r + dr, c + dc
            if (0 <= nr < N and 0 <= nc < M and (nr, nc) not in parent
                    and grid[nr][nc] != 'X'):
                parent[(nr, nc)] = (r, c)
                if nr == end_r and nc == end_c:
                    path, cur = [], (end_r, end_c)
                    while cur is not None:
                        path.append(cur)
                        cur = parent[cur]
                    path.reverse()
                    return dist + 1, path
                queue.append((nr, nc, dist + 1))

    return math.inf, []


# ─────────────────────────────────────────────
# Trip costing
# ─────────────────────────────────────────────

COST_PER_STEP = 5
TIME_PER_STEP = 2

def compute_trip(driver_to_pickup_dist, pickup_to_dest_dist):


# ─────────────────────────────────────────────
# Grid class
# ─────────────────────────────────────────────
class Grid:
  def __init__(self, row, col):
    self.row=row
    self.col = col
    self.grid = [[0 for j in range(col)] for i in range(row)]
  
  def placeRideRequest(self, Passenger):
    self.grid[Passenger.pickup.row][Passenger.pickup.col] = 'P'

  def placeDestination(self, Passenger):
    self.grid[Passenger.destination.row][Passenger.destination.col] = 'R'
  
  def placeDriver(self, driver):
    self.grid[driver.position.row][driver.position.col] = driver.id
  
  def placeObstacle(self, row ,col):
    self.grid[row][col]='X'
  
  def isValid(self, row, col):
      # Check if position is inside grid bounds
        # and not an obstacle
      if 0 <= row < self.row and 0 <= col < self.col and self.grid[row][col] != 'X':
            return True
        return False
  
  def display(self):
    for i in range(self.row):
        for j in range(self.col):
            print(self.grid[i][j], end=" ")
        print()
    

def trip_result(request, assigned_driver, bfs_path1, bfs_path2, cost, travel_time):
    return {
        "request":                request,
        "assigned_driver":        assigned_driver,
        "driver_to_pickup_steps": len(bfs_path1) - 1,
        "pickup_to_dest_steps":   len(bfs_path2) - 1,
        "total_steps":            len(bfs_path1) + len(bfs_path2) - 2,
        "cost":                   cost,
        "travel_time":            travel_time,
        "full_path":              bfs_path1 + bfs_path2[1:]
    }


def trip_calculator(driver, request, bfs_path1, bfs_path2,
                    cost_per_step=5, time_per_step=2):
    total = len(bfs_path1) + len(bfs_path2) - 2
    cost  = total * cost_per_step
    time  = total * time_per_step
    result = trip_result(request, driver, bfs_path1, bfs_path2, cost, time)

    print("=" * 45)
    print(f"  TRIP SUMMARY — {request.id}")
    print("=" * 45)
    print(f"  Driver       : {assigned_driver.name} ({assigned_driver.id})")
    print(f"  Phone        : {assigned_driver.phone}")
    print(f"  Car          : {assigned_driver.car}")
    print("-" * 45)
    print(f"  Driver → Pickup  : {result['driver_to_pickup_steps']} steps")
    print(f"  Pickup → Dest    : {result['pickup_to_dest_steps']} steps")
    print(f"  Total Steps      : {result['total_steps']} steps")
    print("-" * 45)
    print(f"  Cost         : {cost} EGP")
    print(f"  Travel Time  : {time} min")
    print("-" * 45)
    print(f"  Full Path    : {' → '.join(str(cell) for cell in result['full_path'])}")
    print("=" * 45)

    return result
  

  class RideMatchingSystem:

    def __init__(self, grid, drivers, requests):
        # system data
        self.grid = grid
        self.drivers = drivers
        self.requests = requests

        # modules
        self.cost_matrix = CostMatrix(drivers, requests)
        self.dp_assigner = DPAssigner(self.cost_matrix)
        self.dc = DivideAndConquer(grid, drivers)
        self.greedy = GreedySelector()
        self.bfs = BFS(grid)
        self.calculator = TripCalculator()

        # results
        self.results = []

    def run(self):

        # build cost matrix
        self.cost_matrix.compute()
        print("\n=== COST MATRIX ===")
        self.cost_matrix.display()

        # DP assignment
        assignment = self.dp_assigner.get_assignment()
        print("\n=== DP ASSIGNMENT ===")

        for i, request in enumerate(self.requests):

            passenger = request.passenger
            driver = None

            # use DP first
            if i in assignment:
                driver = self.drivers[assignment[i]]
                print(f"R{request.id} → {driver.name} ({driver.id})")

            # fallback to greedy
            if driver is None:
                candidates = self.dc.search(passenger)
                driver = self.greedy.select(candidates, passenger)

            if driver is None:
                continue

            driver.available = False

            # BFS paths
            d2p, path1 = self.bfs.search(driver.position, passenger.pickup)
            p2d, path2 = self.bfs.search(passenger.pickup, passenger.destination)

            total_steps = d2p + p2d
            cost = total_steps * COST_PER_STEP
            time = total_steps * TIME_PER_STEP
            full_path = path1 + path2[1:]

            # save result
            self.results.append({
                "request": request,
                "driver": driver,
                "cost": cost,
                "time": time,
                "path": full_path
            })

            # output
            print(f"\n=== TRIP R{request.id} ===")
            print(f"Driver : {driver.name} ({driver.id})")
            print(f"Car    : {driver.car}")
            print(f"Phone  : {driver.phone}")
            print(f"Steps  : {total_steps}")
            print(f"Cost   : {cost} EGP")
            print(f"Time   : {time} min")
            print(f"Path   : {' → '.join(map(str, full_path))}")
            print("-" * 45)

        return self.results
