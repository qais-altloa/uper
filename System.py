# system.py
# RideMatchingSystem: orchestrates grid, DP assignment, greedy fallback, BFS, and output

import math
from algorithms import (
    bfs, CostMatrix, DPAssigner, GreedySelector,
    COST_PER_STEP, TIME_PER_STEP
)


class RideMatchingSystem:

    def __init__(self, grid, drivers, requests):
        # system data
        self.grid     = grid
        self.drivers  = drivers
        self.requests = requests

        # modules
        self.cost_matrix = CostMatrix(drivers, requests)
        self.dp_assigner = DPAssigner(drivers, requests)
        self.greedy      = GreedySelector()

        # results
        self.results = []

    def run(self):

        # build and display cost matrix
        self.cost_matrix.compute()
        print("\n=== COST MATRIX ===")
        self.cost_matrix.display()

        # DP assignment
        dp_results, total_cost = self.dp_assigner.assign()

        print("\n=== DP ASSIGNMENT ===")
        self.dp_assigner.display(dp_results, total_cost)

        # build a lookup: request id → assigned driver from DP
        dp_map = {r["request"].id: r["driver"] for r in dp_results}

        for request in self.requests:

            passenger = request.passenger
            driver    = dp_map.get(request.id)

            # fallback to greedy if DP gave no result
            if driver is None:
                driver = self.greedy.select(
                    [d for d in self.drivers if d.available],
                    passenger
                )

            if driver is None:
                print(f"  [!] No available driver for request R{request.id} — skipping.")
                continue

            driver.available = False

            # BFS paths
            N, M       = self.grid.row, self.grid.col
            d2p, path1 = bfs(self.grid.grid, N, M,
                             driver.position.row, driver.position.col,
                             passenger.pickup.row, passenger.pickup.col)
            p2d, path2 = bfs(self.grid.grid, N, M,
                             passenger.pickup.row, passenger.pickup.col,
                             passenger.destination.row, passenger.destination.col)

            # guard: no path exists (blocked by obstacles)
            if d2p == math.inf or p2d == math.inf:
                print(f"  [!] No reachable path for request R{request.id} — skipping.")
                driver.available = True   # release the driver back
                continue

            total_steps = d2p + p2d
            cost        = total_steps * COST_PER_STEP
            time        = total_steps * TIME_PER_STEP
            full_path   = path1 + path2[1:]

            # save result
            self.results.append({
                "request": request,
                "driver":  driver,
                "cost":    cost,
                "time":    time,
                "path":    full_path
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
