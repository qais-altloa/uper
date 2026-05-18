# main.py

import os
import time
import random
import math

from models    import Driver, Passenger, RideRequest, Cell
from grid      import Grid
from algorithms import BFS, GreedySelector, DivideAndConquer, DPAssigner


# ── constants ─────────────────────────────────────────────────────────────────

COST_PER_STEP = 5   # EGP per grid step
TIME_PER_STEP = 2   # minutes per grid step

NAMES  = ["Ahmed", "Sara", "Mohamed", "Fatima", "Omar",
          "Laila", "Youssef", "Mariam", "Khaled", "Nour"]
CARS   = ["Toyota Camry", "Honda Civic", "Hyundai Elantra",
          "Kia Cerato", "Nissan Sunny", "Tesla Model 3",
          "BMW 320i", "Mercedes C200", "Audi A4", "Ford Focus"]
PHONES = ["0100", "0111", "0122", "0133", "0144",
          "0155", "0166", "0177", "0188", "0199"]


# ── helpers ───────────────────────────────────────────────────────────────────

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def header():
    print("=" * 60)
    print("   🚕  SMART UBER RIDE MATCHING SYSTEM  🚕")
    print("=" * 60)

def sep(n=60):
    print("=" * n)

def make_driver(id, row, col):
    return Driver(
        id    = id,
        name  = NAMES[id % len(NAMES)],
        phone = PHONES[id % len(PHONES)] + str(random.randint(1000, 9999)),
        car   = CARS[id % len(CARS)],
        row   = row,
        col   = col,
    )


# ── algorithm selector ────────────────────────────────────────────────────────

def pick_algorithm(grid, drivers, num_requests):
    """
    Choose which algorithm to use for driver selection.
    Returns one of: 'dp', 'dc', 'greedy'
    """
    rows, cols = grid.get_size()
    grid_size  = rows * cols
    avail      = sum(1 for d in drivers if d.available)

    if num_requests > 1 and avail >= num_requests:
        return 'dp'
    if grid_size > 5000 or (rows > 30 and cols > 30):
        return 'dc'
    return 'greedy'


# ── core matching logic ───────────────────────────────────────────────────────

def select_driver(grid, drivers, passenger, algo):
    """Return the chosen driver (or None) using the specified algorithm."""
    if algo == 'dc':
        dc = DivideAndConquer(grid)
        return dc.select(drivers, passenger)
    # greedy (default)
    driver, _ = GreedySelector.select(drivers, passenger)
    return driver


def process_trip(grid, driver, passenger, animate=True):
    """
    Run BFS for driver→pickup then pickup→destination.
    Returns result dict or None on failure.
    animate=False skips step-by-step display (used in large grids).
    """
    # driver → pickup
    d1, path1 = BFS.find_path(grid, driver.position, passenger.pickup)
    if d1 == math.inf:
        print(f"  ❌ No path from {driver.name} to pickup {passenger.pickup}")
        return None

    if animate:
        _animate(grid, driver, path1, f"pickup {passenger.pickup}")
    else:
        # just move the driver without displaying every step
        for step in path1:
            grid.update_driver_position(driver, step)

    # pickup → destination
    d2, path2 = BFS.find_path(grid, passenger.pickup, passenger.destination)
    if d2 == math.inf:
        print(f"  ❌ No path from pickup to destination {passenger.destination}")
        return None

    # clear pickup marker
    grid.grid[passenger.pickup.row][passenger.pickup.col] = '0'

    if animate:
        _animate(grid, driver, path2, f"destination {passenger.destination}")
    else:
        for step in path2:
            grid.update_driver_position(driver, step)

    total = d1 + d2
    return {
        'driver'        : driver,
        'dist_to_pickup': d1,
        'dist_to_dest'  : d2,
        'total_distance': total,
        'cost'          : total * COST_PER_STEP,
        'time'          : total * TIME_PER_STEP,
    }


def _animate(grid, driver, path, label):
    print(f"\n🎬 {driver.name} → {label} ...")
    for i, step in enumerate(path, 1):
        grid.update_driver_position(driver, step)
        grid.display(f"Step {i}/{len(path)}  →  {label}")
        time.sleep(0.15)
    print(f"✅ Reached {label}!")


# ── request processing ────────────────────────────────────────────────────────

def process_requests(grid, drivers, requests, animate=True):
    """
    Process all requests, auto-selecting the algorithm.
    Returns list of result dicts.
    """
    algo = pick_algorithm(grid, drivers, len(requests))
    print(f"\n📡 Algorithm selected: {algo.upper()}")

    results = []

    if algo == 'dp' and len(requests) > 1:
        # DP assigns all requests at once
        available_drivers = [d for d in drivers if d.available]
        
        if len(available_drivers) >= len(requests):
            assigner = DPAssigner(drivers, requests)
            assignments, total_cost = assigner.assign()
            
            print(f"   DP total cost: {total_cost} (Manhattan)")
            
            # Process each assignment
            for req_idx, drv_idx in assignments:
                req = requests[req_idx]
                driver = available_drivers[drv_idx]
                _print_request_header(req, driver, algo)
                result = process_trip(grid, driver, req.passenger, animate)
                if result:
                    result['request'] = req
                    driver.available = False
                    results.append(result)
        else:
            # Fallback to greedy if not enough drivers
            print("   Not enough drivers for DP, falling back to greedy...")
            results = _process_greedy(grid, drivers, requests, animate, algo)
    else:
        # Greedy or D&C: process one by one
        results = _process_greedy(grid, drivers, requests, animate, algo)

    return results


def _process_greedy(grid, drivers, requests, animate, algo):
    """Process requests one by one using greedy/D&C selection."""
    results = []
    avail = [d for d in drivers if d.available]
    
    for req in requests:
        driver = select_driver(grid, avail, req.passenger, algo)
        if not driver:
            print(f"\n❌ No driver available for Request {req.id}")
            continue
        _print_request_header(req, driver, algo)
        result = process_trip(grid, driver, req.passenger, animate)
        if result:
            result['request'] = req
            driver.available = False
            avail.remove(driver)
            results.append(result)

        if animate:
            input("\n⏎ Press Enter for next request...")
    
    return results


def _print_request_header(req, driver, algo):
    p = req.passenger
    sep()
    print(f"🔄 Request {req.id}  |  Algorithm: {algo.upper()}")
    print(f"   Pickup      : {p.pickup}")
    print(f"   Destination : {p.destination}")
    print(f"   Driver      : {driver.name} (D{driver.id})  |  {driver.car}  |  {driver.phone}")
    sep()


# ── report ────────────────────────────────────────────────────────────────────

def print_report(results, player_name=""):
    sep(80)
    print("📋  FINAL TRIP REPORT" + (f"  —  {player_name}" if player_name else ""))
    sep(80)

    total_cost = total_time = 0
    for r in results:
        req = r['request']
        drv = r['driver']
        print(f"\n🚕 Trip {req.id}:")
        print(f"   Driver        : {drv.name} (D{drv.id})  |  {drv.car}  |  {drv.phone}")
        print(f"   To pickup     : {r['dist_to_pickup']} steps")
        print(f"   To destination: {r['dist_to_dest']} steps")
        print(f"   Total distance: {r['total_distance']} steps")
        print(f"   Cost          : {r['cost']} EGP")
        print(f"   Time          : {r['time']} min")
        total_cost += r['cost']
        total_time += r['time']

    sep(80)
    print(f"   Trips completed : {len(results)}")
    print(f"   Total cost      : {total_cost} EGP")
    print(f"   Total time      : {total_time} min")
    sep(80)


# ── hard test case (500 × 500) ────────────────────────────────────────────────

def run_hard_test():
    """
    500×500 grid, 20 drivers, 5 simultaneous requests — from the project spec.
    No animation (grid too large to display).
    Uses DP for assignment + BFS for actual path distances.
    """
    clear()
    sep(70)
    print("  🔥  HARD TEST CASE  —  500 × 500 grid, 20 drivers, 5 requests")
    sep(70)

    grid = Grid(500, 500)
    # No obstacles for the spec test so paths are always reachable
    grid.generate_obstacles(0)

    driver_coords = [
        (10,20),(50,60),(100,120),(130,300),(200,200),
        (250,250),(300,100),(320,330),(400,450),(450,100),
        (70,420),(90,90),(160,170),(210,50),(260,400),
        (350,250),(410,210),(470,470),(20,480),(499,10),
    ]
    drivers = []
    for i, (r, c) in enumerate(driver_coords, 1):
        d = make_driver(i, r, c)
        drivers.append(d)
        grid.place_driver(d)

    request_data = [
        (40,50,  100,100),
        (220,210,300,300),
        (480,460,450,430),
        (80,400, 20,350),
        (340,260,410,300),
    ]
    requests = []
    for i, (pr, pc, dr, dc) in enumerate(request_data, 1):
        p = Passenger(pr, pc, dr, dc)
        r = RideRequest(i, p)
        requests.append(r)
        grid.place_passenger(p)
        grid.place_destination(p)

    print("\n🚗 Drivers placed. Running assignment (DP) + BFS paths...\n")
    t0 = time.time()

    results = process_requests(grid, drivers, requests, animate=False)

    elapsed = time.time() - t0
    print_report(results)
    print(f"\n⏱️  Computed in {elapsed:.3f} seconds")

    # Also print the expected spec output for comparison
    sep(70)
    print("📄  Expected output (from project spec — Manhattan distances):")
    spec = [
        ("R1","D2", 20, 110, 130),
        ("R2","D5", 30, 170, 200),
        ("R3","D18",20,  60,  80),
        ("R4","D11",30, 110, 140),
        ("R5","D16",20, 110, 130),
    ]
    for req, drv, d2p, d2d, tot in spec:
        print(f"  {req} → {drv}  |  to pickup: {d2p}  |  to dest: {d2d}  |  total: {tot}")
    sep(70)


# ── interactive game ──────────────────────────────────────────────────────────

class UberGame:
    """Main interactive loop."""

    def __init__(self):
        self.player_name = ""
        self.grid        = None
        self.drivers     = []

    # ── setup ─────────────────────────────────────────────────────────────────

    def _get_name(self):
        header()
        name = input("\n👤 Enter your name: ").strip()
        self.player_name = name or "Guest"
        print(f"\n✨ Hello, {self.player_name}! Welcome to the Uber System! ✨")
        input("\n⏎ Press Enter to continue...")

    def _setup_grid(self):
        clear()
        header()
        print("\n🏙️  CITY GRID SETUP")
        print("-" * 40)

        while True:
            try:
                rows = int(input("Rows    (5–20): "))
                cols = int(input("Columns (5–20): "))
                if 5 <= rows <= 20 and 5 <= cols <= 20:
                    break
                print("❌ Values must be between 5 and 20.")
            except ValueError:
                print("❌ Enter integers.")

        self.grid    = Grid(rows, cols)
        self.drivers = []

        self.grid.generate_obstacles(30)

        while True:
            try:
                n = int(input("Drivers to add (1–10): "))
                if 1 <= n <= 10:
                    break
                print("❌ Between 1 and 10.")
            except ValueError:
                print("❌ Enter an integer.")

        free = self.grid.get_free_positions()
        random.shuffle(free)

        for i in range(min(n, len(free))):
            r, c = free[i]
            d = make_driver(i + 1, r, c)
            self.drivers.append(d)
            self.grid.place_driver(d)

        print(f"\n✅ {len(self.drivers)} drivers placed.")
        self.grid.display("Initial City Grid")
        input("\n⏎ Press Enter to continue...")

    def _collect_requests(self):
        clear()
        header()
        print("\n📱 RIDE REQUESTS")
        print("-" * 40)
        max_req = min(5, len(self.drivers))

        while True:
            try:
                n = int(input(f"Number of requests (1–{max_req}): "))
                if 1 <= n <= max_req:
                    break
                print(f"❌ Between 1 and {max_req}.")
            except ValueError:
                print("❌ Enter an integer.")

        requests = []
        for i in range(n):
            print(f"\n── Request {i+1} ──")
            while True:
                try:
                    pr = int(input("  Pickup row   : "))
                    pc = int(input("  Pickup col   : "))
                    dr = int(input("  Dest   row   : "))
                    dc = int(input("  Dest   col   : "))
                    if not (self.grid.in_bounds(pr, pc) and self.grid.in_bounds(dr, dc)):
                        print("❌ Out of bounds.")
                        continue
                    if self.grid.is_blocked(pr, pc) or self.grid.is_blocked(dr, dc):
                        print("❌ Cannot place on blocked cell.")
                        continue
                    break
                except ValueError:
                    print("❌ Enter integers.")

            p = Passenger(pr, pc, dr, dc)
            requests.append(RideRequest(i + 1, p))
            self.grid.place_passenger(p)
            self.grid.place_destination(p)

        self.grid.display("Grid with all requests")
        input("\n⏎ Press Enter to start matching...")
        return requests

    # ── main loop ─────────────────────────────────────────────────────────────

    def run(self):
        clear()
        header()
        print("\n  1. Play interactive game")
        print("  2. Run 500×500 hard test case")
        choice = input("\nChoose (1/2): ").strip()

        if choice == '2':
            run_hard_test()
            input("\n⏎ Press Enter to exit...")
            return

        # Interactive mode
        self._get_name()

        while True:
            self._setup_grid()
            requests = self._collect_requests()

            clear()
            print("\n🚀 PROCESSING REQUESTS\n")
            results = process_requests(self.grid, self.drivers, requests, animate=True)

            if results:
                print_report(results, self.player_name)
            else:
                print("\n❌ No trips were completed.")

            again = input("\n🎮 Play again? (yes/no): ").strip().lower()
            if again not in ('yes', 'y'):
                break

            # reset for new round
            self.grid    = None
            self.drivers = []

        print(f"\n👋 Thank you, {self.player_name}! Goodbye! 👋\n")


# ── entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    UberGame().run()
