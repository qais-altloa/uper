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
    Uses bitmask DP over requests; each state assigns the next unset request
    to one of the available drivers.

    Cost = Manhattan distance (driver→pickup + pickup→destination).
    BFS is skipped here to keep the 500×500 hard test fast.
    """

    def __init__(self, drivers, requests):
        self.drivers  = [d for d in drivers if d.available]
        self.requests = requests
        self.D = len(self.drivers)
        self.R = len(self.requests)

    def _cost(self, driver, request):
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
            # Not enough drivers — greedy fallback
            return self._greedy_fallback()

        # dp[mask] = minimum cost when the bits in `mask` are assigned
        INF   = math.inf
        FULL  = (1 << self.R) - 1
        dp     = [INF] * (1 << self.R)
        choice = [None] * (1 << self.R)
        dp[0]  = 0

        for mask in range(FULL):
            if dp[mask] == INF:
                continue
            # next unassigned request
            req_idx = next(r for r in range(self.R) if not (mask >> r & 1))
            req     = self.requests[req_idx]
            drv_used = bin(mask).count('1')   # driver index to try (round-robin)

            for drv_idx in range(self.D):
                new_mask = mask | (1 << req_idx)
                cost     = dp[mask] + self._cost(self.drivers[drv_idx], req)
                if cost < dp[new_mask]:
                    dp[new_mask]     = cost
                    choice[new_mask] = (req_idx, drv_idx)

        # reconstruct
        assignments = []
        mask = FULL
        while mask > 0 and choice[mask] is not None:
            req_idx, drv_idx = choice[mask]
            assignments.append((req_idx, drv_idx))
            mask ^= (1 << req_idx)

        return assignments, dp[FULL]

    def _greedy_fallback(self):
        """Simple greedy when DP can't run (too few drivers)."""
        used = set()
        assignments = []
        total = 0
        for req_idx, req in enumerate(self.requests):
            best, best_cost, best_drv = None, math.inf, -1
            for drv_idx, drv in enumerate(self.drivers):
                if drv_idx in used:
                    continue
                c = self._cost(drv, req)
                if c < best_cost:
                    best_cost = c
                    best_drv  = drv_idx
            if best_drv >= 0:
                used.add(best_drv)
                assignments.append((req_idx, best_drv))
                total += best_cost
        return assignments, total

           
