# algorithms.py

import math
from collections import deque
from models import Cell


# ─────────────────────────────────────────────
#  BFS  –  shortest path on grid
# ─────────────────────────────────────────────

def bfs(grid, start: Cell, end: Cell):
    """
    Returns (distance, path) where path is a list of Cell.
    Returns (inf, []) when no path exists.
    """
    if start == end:
        return 0, [start]

    DIRS = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    visited = {(start.row, start.col): None}   # cell -> parent
    queue = deque([(start.row, start.col, 0)])

    while queue:
        r, c, dist = queue.popleft()

        for dr, dc in DIRS:
            nr, nc = r + dr, c + dc
            if (grid.in_bounds(nr, nc)
                    and not grid.is_blocked(nr, nc)
                    and (nr, nc) not in visited):

                visited[(nr, nc)] = (r, c)

                if nr == end.row and nc == end.col:
                    # reconstruct
                    path, cur = [], (nr, nc)
                    while cur is not None:
                        path.append(Cell(cur[0], cur[1]))
                        cur = visited[cur]
                    path.reverse()
                    return dist + 1, path

                queue.append((nr, nc, dist + 1))

    return math.inf, []


# ─────────────────────────────────────────────
#  GREEDY  –  pick nearest available driver
# ─────────────────────────────────────────────

def greedy_select(drivers, pickup: Cell):
    """
    Returns the best available driver using a combined score:
        score = distance + (5.0 - rating) * 2
    Lower is better, so high-rated nearby drivers win.
    Returns None when no driver is available.
    """
    best, best_score = None, math.inf
    for driver in drivers:
        if not driver.available:
            continue
        distance      = driver.position.manhattan(pickup)
        rating_penalty = (5.0 - driver.rating) * 2   # 0 at 5-star, up to 8 at 1-star
        score = distance + rating_penalty
        if score < best_score:
            best_score = score
            best = driver
    return best


# ─────────────────────────────────────────────
#  DIVIDE & CONQUER  –  region-based search
# ─────────────────────────────────────────────

def dc_select(drivers, pickup: Cell, grid_rows, grid_cols):
    """
    Splits the grid into 4 quadrants.
    First searches the quadrant that contains the pickup point.
    Falls back to all other quadrants if nothing is found there.
    Returns the nearest available driver (or None).
    """
    mid_r = grid_rows // 2
    mid_c = grid_cols // 2

    def quadrant(cell):
        above = cell.row < mid_r
        left  = cell.col < mid_c
        if above and left:   return 0   # top-left
        if above:            return 1   # top-right
        if left:             return 2   # bottom-left
        return 3                        # bottom-right

    def nearest_in(quad):
        best, best_dist = None, math.inf
        for driver in drivers:
            if driver.available and quadrant(driver.position) == quad:
                d = driver.position.manhattan(pickup)
                if d < best_dist:
                    best_dist = d
                    best = driver
        return best

    home_quad = quadrant(pickup)
    found = nearest_in(home_quad)
    if found:
        return found

    # search all other quadrants, return overall nearest
    best, best_dist = None, math.inf
    for q in range(4):
        if q == home_quad:
            continue
        candidate = nearest_in(q)
        if candidate:
            d = candidate.position.manhattan(pickup)
            if d < best_dist:
                best_dist = d
                best = candidate
    return best


# ─────────────────────────────────────────────
#  DYNAMIC PROGRAMMING  –  optimal assignment
#  for multiple simultaneous requests
# ─────────────────────────────────────────────

def dp_assign(drivers, requests):
    """
    Assigns each request to a *unique* driver so the total trip cost
    (Manhattan: driver→pickup + pickup→destination) is minimised.

    Uses bitmask DP where the mask tracks which *drivers* are already used.
    Requests are processed in order (0, 1, 2 …); for each we try every
    still-available driver.

    Returns a list of (request, driver) pairs in request order.
    Assumes len(drivers) >= len(requests).
    """
    R = len(requests)
    D = len(drivers)

    # cost[d][r]
    cost = [
        [
            drivers[d].position.manhattan(requests[r].pickup)
            + requests[r].pickup.manhattan(requests[r].destination)
            for r in range(R)
        ]
        for d in range(D)
    ]

    INF = math.inf
    # dp[mask] = min total cost when the set of used drivers == mask
    #            and we have already assigned the first popcount(mask) requests
    dp     = [INF] * (1 << D)
    parent = [None] * (1 << D)
    dp[0]  = 0

    for mask in range(1 << D):
        if dp[mask] == INF:
            continue
        r = bin(mask).count('1')   # next request index to assign
        if r >= R:
            continue
        for d in range(D):
            if mask >> d & 1:      # driver d already used
                continue
            new_mask = mask | (1 << d)
            new_cost = dp[mask] + cost[d][r]
            if new_cost < dp[new_mask]:
                dp[new_mask] = new_cost
                parent[new_mask] = (mask, d, r)

    # Find the best final mask (exactly R drivers used)
    best_mask, best_cost = -1, INF
    for mask in range(1 << D):
        if bin(mask).count('1') == R and dp[mask] < best_cost:
            best_cost = dp[mask]
            best_mask = mask

    # Reconstruct
    assignments = [None] * R
    mask = best_mask
    while parent[mask] is not None:
        prev_mask, d, r = parent[mask]
        assignments[r] = (requests[r], drivers[d])
        mask = prev_mask

    return assignments
