# algorithms.py

import math
from collections import deque
from models import Cell


# ── BFS ──────────────────────────────────────────────────────────────────────

class BFS:
    """Shortest-path finder on the grid."""

    DIRS = [(0, 1), (0, -1), (1, 0), (-1, 0)]

    @staticmethod
    def find_path(grid, start, end):
        """
        Returns (distance, path) or (math.inf, []) if unreachable.
        distance is the number of steps (edges), path is a list of Cell.
        """
        if start == end:
            return 0, [start]

        N, M   = grid.get_size()
        parent = {(start.row, start.col): None}
        queue  = deque([(start.row, start.col, 0)])

        while queue:
            r, c, dist = queue.popleft()

            for dr, dc in BFS.DIRS:
                nr, nc = r + dr, c + dc
                if (0 <= nr < N and 0 <= nc < M
                        and (nr, nc) not in parent
                        and not grid.is_blocked(nr, nc)):

                    parent[(nr, nc)] = (r, c)

                    if nr == end.row and nc == end.col:
                        # reconstruct path
                        path, cur = [], (nr, nc)
                        while cur is not None:
                            path.append(Cell(cur[0], cur[1]))
                            cur = parent[cur]
                        path.reverse()
                        return dist + 1, path

                    queue.append((nr, nc, dist + 1))

        return math.inf, []


# ── Greedy ───────────────────────────────────────────────────────────────────

class GreedySelector:
    """Pick the nearest available driver by Manhattan distance."""

    @staticmethod
    def select(drivers, passenger):
        """Returns (best_driver, manhattan_distance) or (None, inf)."""
        best, best_dist = None, math.inf
        for d in drivers:
            if d.available:
                dist = d.position.manhattan(passenger.pickup)
                if dist < best_dist:
                    best_dist = dist
                    best = d
        return best, best_dist


# ── Divide & Conquer ─────────────────────────────────────────────────────────

class DivideAndConquer:
    """
    Split the grid into 4 quadrants.
    Search the passenger's quadrant first; fall back to others if empty.
    """

    def __init__(self, grid):
        self.rows, self.cols = grid.get_size()

    def _quadrant(self, pos):
        mid_r = self.rows // 2
        mid_c = self.cols // 2
        top   = pos.row < mid_r
        left  = pos.col < mid_c
        if   top  and left:  return 0   # top-left
        elif top:            return 1   # top-right
        elif left:           return 2   # bottom-left
        else:                return 3   # bottom-right

    def _nearest_in(self, drivers, passenger, quadrant):
        best, best_dist = None, math.inf
        for d in drivers:
            if d.available and self._quadrant(d.position) == quadrant:
                dist = d.position.manhattan(passenger.pickup)
                if dist < best_dist:
                    best_dist = dist
                    best = d
        return best, best_dist

    def select(self, drivers, passenger):
        """Returns the nearest available driver."""
        q = self._quadrant(passenger.pickup)

        # same quadrant first
        driver, _ = self._nearest_in(drivers, passenger, q)
        if driver:
            return driver

        # combine results from other quadrants
        best, best_dist = None, math.inf
        for other_q in range(4):
            if other_q == q:
                continue
            d, dist = self._nearest_in(drivers, passenger, other_q)
            if d and dist < best_dist:
                best_dist = dist
                best = d
        return best


# ── Dynamic Programming ───────────────────────────────────────────────────────

class DPAssigner:
    """
    Optimal 1-to-1 assignment of N requests to N drivers.
    Uses bitmask DP: iterates over request masks, assigns available drivers in order.
    Cost = Manhattan distance (driver→pickup + pickup→destination).
    """

    def __init__(self, drivers, requests):
        self.drivers = [d for d in drivers if d.available]
        self.requests = requests
        self.D = len(self.drivers)
        self.R = len(self.requests)

    def _cost(self, driver, request):
        """Calculate Manhattan distance cost for a driver-request pair."""
        p = request.passenger
        return (driver.position.manhattan(p.pickup) +
                p.pickup.manhattan(p.destination))

    def assign(self):
        """
        Returns list of (request_index, driver_index) pairs and total cost.
        Falls back to greedy if not enough drivers.
        """
        if self.R == 0 or self.D == 0:
            return [], 0

        if self.D < self.R:
            # Not enough available drivers - use greedy fallback
            return self._greedy_fallback()

        INF = math.inf
        FULL = (1 << self.R) - 1
        
        # dp[mask] = minimum cost to assign requests represented by mask
        # using drivers[0 .. count_bits(mask)-1]
        dp = [INF] * (1 << self.R)
        choice = [None] * (1 << self.R)  # stores (request_idx, driver_idx) for the last assignment
        dp[0] = 0

        # Iterate over all request masks
        for mask in range(FULL + 1):
            if dp[mask] == INF:
                continue
            
            assigned_count = bin(mask).count('1')
            if assigned_count >= self.D:
                continue
            
            # The next driver to assign (in order)
            driver = self.drivers[assigned_count]
            
            # Try assigning this driver to each unassigned request
            for req_idx in range(self.R):
                if mask & (1 << req_idx):
                    continue  # Request already assigned
                
                new_mask = mask | (1 << req_idx)
                new_cost = dp[mask] + self._cost(driver, self.requests[req_idx])
                
                if new_cost < dp[new_mask]:
                    dp[new_mask] = new_cost
                    choice[new_mask] = (req_idx, assigned_count)

        # Reconstruct assignments
        assignments = []
        if dp[FULL] != INF:
            mask = FULL
            while mask > 0:
                req_idx, drv_idx = choice[mask]
                assignments.append((req_idx, drv_idx))
                mask ^= (1 << req_idx)
            assignments.reverse()  # Restore original order
            return assignments, dp[FULL]
        
        # Fallback if DP fails
        return self._greedy_fallback()

    def _greedy_fallback(self):
        """Simple greedy assignment when DP can't run (e.g., too few drivers)."""
        used_drivers = set()
        assignments = []
        total_cost = 0
        
        # Sort requests arbitrarily (by index)
        for req_idx, req in enumerate(self.requests):
            best_drv_idx = -1
            best_cost = math.inf
            
            # Find best available driver for this request
            for drv_idx, drv in enumerate(self.drivers):
                if drv_idx in used_drivers:
                    continue
                cost = self._cost(drv, req)
                if cost < best_cost:
                    best_cost = cost
                    best_drv_idx = drv_idx
            
            if best_drv_idx >= 0:
                used_drivers.add(best_drv_idx)
                assignments.append((req_idx, best_drv_idx))
                total_cost += best_cost
        
        return assignments, total_cost

           
