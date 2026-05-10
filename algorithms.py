# algorithms.py
# All algorithm classes: BFS, cost helpers, CostMatrix, DPAssigner, GreedySelector

import math
from collections import deque

DIRECTIONS = [(0, 1), (0, -1), (1, 0), (-1, 0)]

COST_PER_STEP = 5
TIME_PER_STEP = 2


# ─────────────────────────────────────────────
# BFS shortest path
# ─────────────────────────────────────────────

def bfs(grid, N, M, start_r, start_c, end_r, end_c):
    """
    BFS shortest path on an N×M grid, avoiding 'X' obstacle cells.
    """
    # guard: start or end outside grid
    if not (0 <= start_r < N and 0 <= start_c < M):
        raise ValueError(f"BFS start ({start_r},{start_c}) is outside grid ({N}x{M})")
    if not (0 <= end_r < N and 0 <= end_c < M):
        raise ValueError(f"BFS end ({end_r},{end_c}) is outside grid ({N}x{M})")

    if (start_r, start_c) == (end_r, end_c):
        return 0, [(start_r, start_c)]

    parent = {(start_r, start_c): None}
    queue  = deque([(start_r, start_c, 0)])

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

    return math.inf, []   # no path (blocked by obstacles)


# ─────────────────────────────────────────────
# Trip costing helpers
# ─────────────────────────────────────────────

def compute_trip(driver_to_pickup_dist, pickup_to_dest_dist):
    total_steps = driver_to_pickup_dist + pickup_to_dest_dist
    cost        = total_steps * COST_PER_STEP
    time        = total_steps * TIME_PER_STEP
    return total_steps, cost, time


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
    total  = len(bfs_path1) + len(bfs_path2) - 2
    cost   = total * cost_per_step
    time   = total * time_per_step
    result = trip_result(request, driver, bfs_path1, bfs_path2, cost, time)

    print("=" * 45)
    print(f"  TRIP SUMMARY — {request.id}")
    print("=" * 45)
    print(f"  Driver       : {driver.name} ({driver.id})")
    print(f"  Phone        : {driver.phone}")
    print(f"  Car          : {driver.car}")
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


# ─────────────────────────────────────────────
# CostMatrix
# ─────────────────────────────────────────────

class CostMatrix:
    def __init__(self, drivers, requests):
        self.drivers  = drivers
        self.requests = requests
        self.matrix   = []

    def compute(self):
        for driver in self.drivers:
            row = []
            for request in self.requests:
                pickup = request.passenger.pickup
                cost = (
                    abs(driver.position.row - pickup.row) +
                    abs(driver.position.col - pickup.col)
                )
                row.append(cost)
            self.matrix.append(row)

    def get_cost(self, driver_index, request_index):
        return self.matrix[driver_index][request_index]

    def display(self):
        print("Cost Matrix:\n")
        for row in self.matrix:
            print(row)


# ─────────────────────────────────────────────
# DPAssigner
# ─────────────────────────────────────────────

class DPAssigner:

    COST_PER_STEP = 5
    TIME_PER_STEP = 2

    def __init__(self, drivers, requests):
        # guard: cannot assign with empty lists
        if not drivers:
            raise ValueError("DPAssigner requires at least one driver")
        if not requests:
            raise ValueError("DPAssigner requires at least one request")
        self.drivers  = drivers
        self.requests = requests
        self.R = len(requests)
        self.D = len(drivers)

        self._dp     = {}
        self._choice = {}

    # ─────────────────────────────────────────

    @staticmethod
    def _manhattan(r1, c1, r2, c2):
        return abs(r1 - r2) + abs(c1 - c2)

    # ─────────────────────────────────────────

    def _trip_cost(self, start_r, start_c, req_idx):

        req    = self.requests[req_idx]
        pickup = req.passenger.pickup
        dest   = req.passenger.destination

        to_pickup = self._manhattan(start_r, start_c, pickup.row, pickup.col)
        to_dest   = self._manhattan(pickup.row, pickup.col, dest.row, dest.col)

        return to_pickup + to_dest

    # ─────────────────────────────────────────

    def _reconstruct(self):

        assignments = []
        mask = (1 << self.R) - 1

        while mask != 0:
            req_idx, drv_idx = self._choice[mask]
            assignments.append((req_idx, drv_idx))
            mask ^= (1 << req_idx)

        assignments.reverse()
        return assignments

    # ─────────────────────────────────────────

    def assign(self):

        full_mask = (1 << self.R) - 1

        self._dp[0]     = 0
        self._choice[0] = None

        drv_pos_cache = {
            0: {
                d: (self.drivers[d].position.row, self.drivers[d].position.col)
                for d in range(self.D)
            }
        }

        for mask in range(full_mask + 1):

            if mask not in self._dp:
                continue

            cur_cost = self._dp[mask]
            cur_pos  = drv_pos_cache[mask]

            next_req = next(
                (r for r in range(self.R) if not (mask >> r & 1)),
                -1
            )

            if next_req == -1:
                continue

            for d in range(self.D):

                dr, dc   = cur_pos[d]
                trip     = self._trip_cost(dr, dc, next_req)
                new_cost = cur_cost + trip
                new_mask = mask | (1 << next_req)

                if new_mask not in self._dp or new_cost < self._dp[new_mask]:

                    self._dp[new_mask]     = new_cost
                    self._choice[new_mask] = (next_req, d)

                    new_pos    = dict(cur_pos)
                    dest       = self.requests[next_req].passenger.destination
                    new_pos[d] = (dest.row, dest.col)

                    drv_pos_cache[new_mask] = new_pos

        assignment_path = self._reconstruct()

        drv_pos = {
            d: (self.drivers[d].position.row, self.drivers[d].position.col)
            for d in range(self.D)
        }

        results = []

        for req_idx, drv_idx in assignment_path:

            drv    = self.drivers[drv_idx]
            req    = self.requests[req_idx]
            dr, dc = drv_pos[drv_idx]

            pickup = req.passenger.pickup
            dest   = req.passenger.destination

            d2p = self._manhattan(dr, dc, pickup.row, pickup.col)
            p2d = self._manhattan(pickup.row, pickup.col, dest.row, dest.col)

            total = d2p + p2d

            results.append({
                "request":          req,
                "driver":           drv,
                "driver_to_pickup": d2p,
                "pickup_to_dest":   p2d,
                "total_distance":   total,
                "trip_cost":        total * self.COST_PER_STEP,
                "travel_time":      total * self.TIME_PER_STEP,
            })

            drv_pos[drv_idx] = (dest.row, dest.col)

        results.sort(key=lambda x: x["request"].id)

        return results, self._dp[full_mask]

    # ─────────────────────────────────────────

    def display(self, results, total_cost):

        print("=" * 50)
        print("     DP OPTIMAL ASSIGNMENT RESULTS")
        print("=" * 50)

        for r in results:

            req = r["request"]
            drv = r["driver"]

            print(f"\nRequest R{req.id} -> Driver {drv.id} ({drv.name})")
            print(f"  Driver start pos     : ({drv.position.row}, {drv.position.col})")
            print(f"  Pickup               : ({req.passenger.pickup.row}, {req.passenger.pickup.col})")
            print(f"  Destination          : ({req.passenger.destination.row}, {req.passenger.destination.col})")
            print(f"  Driver -> Pickup dist: {r['driver_to_pickup']}")
            print(f"  Pickup -> Dest dist  : {r['pickup_to_dest']}")
            print(f"  Total distance       : {r['total_distance']}")
            print(f"  Trip cost            : ${r['trip_cost']}")
            print(f"  Travel time          : {r['travel_time']} min")

        print("\n" + "=" * 50)
        print(f"  TOTAL SYSTEM DISTANCE : {total_cost}")
        print("=" * 50)


# ─────────────────────────────────────────────
# GreedySelector
# ─────────────────────────────────────────────

class GreedySelector:

    def __init__(self):
        pass

    def grid_distance(self, driver, passenger):
        """
        Calculate steps between driver and pickup location
        using grid movement (row + col differences)
        """
        row_steps = abs(driver.position.row - passenger.pickup.row)
        col_steps = abs(driver.position.col - passenger.pickup.col)
        return row_steps + col_steps

    def select(self, drivers, passenger):
        """
        Choose the closest available driver
        """
        best_driver  = None
        min_distance = math.inf

        for driver in drivers:

            if not driver.available:
                continue

            current_distance = self.grid_distance(driver, passenger)

            if current_distance < min_distance:
                min_distance = current_distance
                best_driver  = driver
            elif current_distance == min_distance:
                best_driver = driver   # tie: last wins

        return best_driver
