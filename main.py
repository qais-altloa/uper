# main.py

import math
import random

from models import Driver, Request
from grid import Grid
from algorithms import bfs, greedy_select, dc_select, dp_assign

# ── constants ────────────────────────────────
COST_PER_STEP = 5   # EGP
TIME_PER_STEP = 2   # minutes


# ─────────────────────────────────────────────
#  Input helpers
# ─────────────────────────────────────────────

def read_int(prompt, lo=None, hi=None):
    while True:
        try:
            v = int(input(prompt))
            if (lo is None or v >= lo) and (hi is None or v <= hi):
                return v
            print(f"  Please enter a value between {lo} and {hi}.")
        except ValueError:
            print("  Invalid input, try again.")


def read_cell(prompt, grid):
    print(prompt)
    while True:
        r = read_int(f"  row    (0-{grid.rows-1}): ", 0, grid.rows - 1)
        c = read_int(f"  column (0-{grid.cols-1}): ", 0, grid.cols - 1)
        if grid.is_blocked(r, c):
            print("  That cell is blocked (X). Choose another.")
        else:
            return r, c


# ─────────────────────────────────────────────
#  Trip processing
# ─────────────────────────────────────────────

def process_trip(grid, driver, request, algo_name):
    """
    Runs BFS for driver->pickup and pickup->destination.
    Shows fare estimate and asks passenger to confirm (cancellation point).
    Asks for a rating after a completed trip.
    Returns a result dict, or None on failure / cancellation.
    """
    print(f"\n  Algorithm used : {algo_name}")
    print(f"  Assigned driver: D{driver.id} – {driver.name}  "
          f"| Rating: {driver.rating}/5.0  | Position: {driver.position}")

    # driver -> pickup
    d1, path1 = bfs(grid, driver.position, request.pickup)
    if d1 == math.inf:
        print("  ERROR: No path from driver to pickup (blocked grid).")
        return None

    # pickup -> destination
    d2, path2 = bfs(grid, request.pickup, request.destination)
    if d2 == math.inf:
        print("  ERROR: No path from pickup to destination (blocked grid).")
        return None

    total = d1 + d2
    cost  = total * COST_PER_STEP
    time_ = total * TIME_PER_STEP

    print(f"  Driver -> Pickup  : {d1} steps  |  path: {' -> '.join(str(p) for p in path1)}")
    print(f"  Pickup -> Dest    : {d2} steps  |  path: {' -> '.join(str(p) for p in path2)}")
    print(f"  Total distance    : {total} steps")
    print(f"  Estimated cost    : {cost} EGP")
    print(f"  Estimated time    : {time_} minutes")

    # ── Cancellation check ───────────────────────────────────
    confirm = input("  Confirm ride? (yes/no): ").strip().lower()
    if confirm not in ("yes", "y"):
        print("  Ride cancelled. Driver is available again.")
        return None                         # driver stays available

    # ── Trip completed – ask for rating ─────────────────────
    driver.available = False
    print("  Ride completed!")

    while True:
        try:
            stars = int(input(f"  Rate driver {driver.name} (1-5): "))
            if 1 <= stars <= 5:
                driver.add_rating(stars)
                print(f"  New rating for {driver.name}: {driver.rating}/5.0")
                break
            print("  Please enter a number between 1 and 5.")
        except ValueError:
            print("  Invalid input.")

    return {"request": request, "driver": driver,
            "d_to_pickup": d1, "d_to_dest": d2,
            "total": total, "cost": cost, "time": time_,
            "cancelled": False}


# ─────────────────────────────────────────────
#  Algorithm selector
# ─────────────────────────────────────────────

def select_algorithm(drivers, requests, grid):
    """
    Decides which algorithm to use:
      - 1 request           → Greedy
      - Large grid (>900)   → Divide & Conquer
      - Multiple requests   → DP
    """
    if len(requests) > 1:
        return "DP"
    if grid.rows * grid.cols > 900:
        return "Divide & Conquer"
    return "Greedy"


def run_algorithm(algo, drivers, requests, grid):
    """
    Runs the chosen algorithm and returns a list of result dicts.
    """
    available = [d for d in drivers if d.available]

    if algo == "DP":
        if len(available) < len(requests):
            print(f"\n  Not enough drivers ({len(available)}) for {len(requests)} requests.")
            print("  Falling back to Greedy per request.\n")
            algo = "Greedy (fallback)"

    if algo == "DP":
        assignments = dp_assign(available, requests)
        results = []
        for req, drv in assignments:
            print(f"\n--- Request R{req.id} ---")
            r = process_trip(grid, drv, req, "DP")
            if r:
                results.append(r)
        return results

    if algo == "Divide & Conquer":
        results = []
        for req in requests:
            print(f"\n--- Request R{req.id} ---")
            drv = dc_select([d for d in drivers if d.available],
                            req.pickup, grid.rows, grid.cols)
            if drv is None:
                print("  No available driver found.")
                continue
            r = process_trip(grid, drv, req, "Divide & Conquer")
            if r:
                results.append(r)
        return results

    # Greedy (default / fallback)
    results = []
    for req in requests:
        print(f"\n--- Request R{req.id} ---")
        drv = greedy_select([d for d in drivers if d.available], req.pickup)
        if drv is None:
            print("  No available driver found.")
            continue
        r = process_trip(grid, drv, req, algo)
        if r:
            results.append(r)
    return results


# ─────────────────────────────────────────────
#  Summary report
# ─────────────────────────────────────────────

def print_report(results):
    print("\n" + "=" * 50)
    print("  FINAL SUMMARY")
    print("=" * 50)
    for res in results:
        req = res["request"]
        drv = res["driver"]
        print(f"  R{req.id} -> D{drv.id} ({drv.name})  | Rating: {drv.rating}/5.0")
        print(f"      Driver->Pickup : {res['d_to_pickup']} steps")
        print(f"      Pickup->Dest   : {res['d_to_dest']} steps")
        print(f"      Total          : {res['total']} steps")
        print(f"      Cost           : {res['cost']} EGP")
        print(f"      Time           : {res['time']} min")
        print()
    print("=" * 50)


# ─────────────────────────────────────────────
#  Setup helpers
# ─────────────────────────────────────────────

DRIVER_NAMES = ["Ahmed", "Sara", "Mohamed", "Fatima", "Omar",
                "Laila", "Youssef", "Mariam", "Khaled", "Nour"]


def setup_grid():
    print("\n-- Grid Setup --")
    rows = read_int("Rows    (5-30): ", 5, 30)
    cols = read_int("Columns (5-30): ", 5, 30)
    grid = Grid(rows, cols)

    # random obstacles ~25 %
    total = rows * cols
    for _ in range(total // 4):
        r = random.randint(0, rows - 1)
        c = random.randint(0, cols - 1)
        grid.add_obstacle(r, c)

    return grid


def setup_drivers(grid):
    print("\n-- Driver Setup --")
    n = read_int("Number of drivers (1-10): ", 1, 10)

    free = [(r, c)
            for r in range(grid.rows)
            for c in range(grid.cols)
            if grid.is_free(r, c)]
    random.shuffle(free)

    drivers = []
    for i in range(min(n, len(free))):
        r, c = free[i]
        drv = Driver(i + 1, DRIVER_NAMES[i % len(DRIVER_NAMES)], r, c)
        drivers.append(drv)
        grid.place(r, c, f"D{drv.id}")

    print(f"Placed {len(drivers)} driver(s).")
    return drivers


def setup_requests(grid, max_requests):
    print("\n-- Ride Requests --")
    n = read_int(f"Number of requests (1-{max_requests}): ", 1, max_requests)
    requests = []
    for i in range(n):
        print(f"\nRequest {i+1}:")
        pr, pc = read_cell("  Pickup location:", grid)
        dr, dc = read_cell("  Destination:", grid)
        req = Request(i + 1, pr, pc, dr, dc)
        requests.append(req)
        grid.place(pr, pc, 'P')
        grid.place(dr, dc, 'R')
    return requests


# ─────────────────────────────────────────────
#  Main
# ─────────────────────────────────────────────

def run_hard_test():
    """Hard test case from the project PDF: 500x500 grid, 20 drivers, 5 requests."""
    print("\n" + "=" * 50)
    print("  HARD TEST CASE  (500x500, 20 drivers, 5 requests)")
    print("=" * 50)

    grid = Grid(500, 500)   # no obstacles so BFS == Manhattan

    drivers_data = [
        (1,"D1",10,20),(2,"D2",50,60),(3,"D3",100,120),(4,"D4",130,300),
        (5,"D5",200,200),(6,"D6",250,250),(7,"D7",300,100),(8,"D8",320,330),
        (9,"D9",400,450),(10,"D10",450,100),(11,"D11",70,420),(12,"D12",90,90),
        (13,"D13",160,170),(14,"D14",210,50),(15,"D15",260,400),(16,"D16",350,250),
        (17,"D17",410,210),(18,"D18",470,470),(19,"D19",20,480),(20,"D20",499,10),
    ]
    requests_data = [
        (1,40,50,100,100),(2,220,210,300,300),
        (3,480,460,450,430),(4,80,400,20,350),(5,340,260,410,300),
    ]

    drivers  = [Driver(d, n, r, c) for d, n, r, c in drivers_data]
    requests = [Request(i, pr, pc, dr, dc) for i, pr, pc, dr, dc in requests_data]

    # Force equal ratings so pure distance decides (matches PDF)
    for drv in drivers:
        drv.rating = 5.0

    print("\nDrivers placed. Running DP assignment...\n")

    assignments = dp_assign(drivers, requests)

    results = []
    for req, drv in assignments:
        d1 = drv.position.manhattan(req.pickup)
        d2 = req.pickup.manhattan(req.destination)
        total = d1 + d2
        cost  = total * COST_PER_STEP
        time_ = total * TIME_PER_STEP
        drv.available = False
        results.append({
            "request": req, "driver": drv,
            "d_to_pickup": d1, "d_to_dest": d2,
            "total": total, "cost": cost, "time": time_,
        })

    print_report(results)


def main():
    print("=" * 50)
    print("   SMART UBER RIDE MATCHING SYSTEM")
    print("=" * 50)

    name = input("Enter your name: ").strip() or "Guest"
    print(f"Hello, {name}!\n")

    while True:
        print("\nWhat would you like to do?")
        print("  1. Start a new ride session")
        print("  2. Run hard test case (500x500)")
        print("  3. Exit")

        choice = read_int("Choose (1/2/3): ", 1, 3)

        if choice == 3:
            break

        if choice == 2:
            run_hard_test()
            continue

        # choice == 1: normal session
        grid    = setup_grid()
        drivers = setup_drivers(grid)
        grid.display("City Grid")

        requests = setup_requests(grid, max_requests=min(5, len(drivers)))
        grid.display("Grid with Requests")

        algo = select_algorithm(drivers, requests, grid)
        print(f"\nSelected algorithm: {algo}")

        results = run_algorithm(algo, drivers, requests, grid)

        if results:
            print_report(results)
        else:
            print("\nNo trips were completed.")

    print(f"\nGoodbye, {name}!")


if __name__ == "__main__":
    main()
