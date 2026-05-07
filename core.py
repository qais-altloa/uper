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
    if driver_to_pickup_dist == math.inf or pickup_to_dest_dist == math.inf:
        raise ValueError(
            f"No valid path found — cannot compute trip cost. "
            f"(driver→pickup: {driver_to_pickup_dist}, "
            f"pickup→dest: {pickup_to_dest_dist})"
        )
    total_steps = driver_to_pickup_dist + pickup_to_dest_dist
    return {
        "total_steps": total_steps,
        "trip_cost": total_steps * COST_PER_STEP,
        "travel_time": total_steps * TIME_PER_STEP,
    }



  

  
