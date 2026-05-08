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
  
  def placeRideRequest(self, RideRequest):
    self.grid[RideRequest.pickup.row][RideRequest.pickup.col] = 'P'

  def placeDestination(self, RideRequest):
    self.grid[RideRequest.destination.row][RideRequest.destination.col] = 'R'
  
  def placeDriver(self, driver):
    self.grid[driver.position.row][driver.position.col] = driver.id
  
  def placeObstacle(self, row ,col):
    self.grid[row][col]='X'
  
  def isValid(self, row, col):
        if 0 <= row < self.row and 0 <= col < self.col and self.grid[row][col] != 'X':
            return True
        return False
  
  def display(self):
    for i in range(self.row):
        for j in range(self.col):
            print(self.grid[i][j], end=" ")
        print()
    


  

  
