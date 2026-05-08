import math
from models import Cell , Driver , Passenger , RideRequest


class CostMatrix:
    def __init__(self, drivers, requests):
        self.drivers = drivers
        self.requests = requests
        self.matrix = []

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



class DPAssigner:

    COST_PER_STEP = 5
    TIME_PER_STEP = 2

    def __init__(self, drivers, requests):
        self.drivers = drivers
        self.requests = requests
        self.R = len(requests)
        self.D = len(drivers)

        self._dp = {}
        self._choice = {}

    # ─────────────────────────────────────────

    @staticmethod
    def _manhattan(r1, c1, r2, c2):
        return abs(r1 - r2) + abs(c1 - c2)

    # ─────────────────────────────────────────

    def _trip_cost(self, start_r, start_c, req_idx):

        req = self.requests[req_idx]

        pickup = req.passenger.pickup
        dest = req.passenger.destination

        to_pickup = self._manhattan(
            start_r,
            start_c,
            pickup.row,
            pickup.col
        ) # driver to pickup

        to_dest = self._manhattan(
            pickup.row,
            pickup.col,
            dest.row,
            dest.col
        ) # pickup to destination

        return to_pickup + to_dest

    # ─────────────────────────────────────────

    def _reconstruct(self):

        assignments = []

        mask = (1 << self.R) - 1 # R = 3 then mask is 111

        while mask != 0:

            req_idx, drv_idx = self._choice[mask] # _choice[111] = (2,0) request 2 to driver 0

            assignments.append((req_idx, drv_idx))

            mask ^= (1 << req_idx) # remove the request

        assignments.reverse() # because we traced backwards 111 - 011 - 001

        return assignments # list of tuples with ((request_index,driver_index)

    # ─────────────────────────────────────────

    def assign(self):

        full_mask = (1 << self.R) - 1

        self._dp[0] = 0
        self._choice[0] = None # empty stat no assignment yet

        drv_pos_cache = { #  this stores position of the driver for every mask {0:(0,0), 1:(5,5)}
            0: {
                d: (
                    self.drivers[d].position.row,
                    self.drivers[d].position.col
                )
                for d in range(self.D)
            }
        }

        for mask in range(full_mask + 1): # loop through masks

            if mask not in self._dp:
                continue

            cur_cost = self._dp[mask]
            cur_pos = drv_pos_cache[mask] # {driver_index :(row,column)}

            next_req = next( # find first unassigned request if mask 101 R0 & R2 done so R1 still not signed
                (
                    r for r in range(self.R)
                    if not (mask >> r & 1) # 101 >> 1 = 010 & 1  = 0 so R1 not signed
                ),
                -1 # all signed
            )

            if next_req == -1:
                continue

            for d in range(self.D): # assigning next request to every driver

                dr, dc = cur_pos[d] #(row,column)

                trip = self._trip_cost(dr, dc, next_req) # start-> pick & pick -> end

                new_cost = cur_cost + trip

                new_mask = mask | (1 << next_req) # 101  new_request is 1 <<  010 | 101 = 111 all request assigned

                if (
                    new_mask not in self._dp or
                    new_cost < self._dp[new_mask]
                ):

                    self._dp[new_mask] = new_cost

                    self._choice[new_mask] = (
                        next_req,
                        d
                    )

                    new_pos = dict(cur_pos) # {dir_index : (row,column)}

                    dest = self.requests[next_req].passenger.destination

                    new_pos[d] = (
                        dest.row,
                        dest.col
                    )

                    drv_pos_cache[new_mask] = new_pos # drv_pos[3] = {new_driver : (row,column)}

        assignment_path = self._reconstruct()

        drv_pos = {
            d: (
                self.drivers[d].position.row,
                self.drivers[d].position.col
            )
            for d in range(self.D)
        }

        results = []

        for req_idx, drv_idx in assignment_path:

            drv = self.drivers[drv_idx]
            req = self.requests[req_idx]

            dr, dc = drv_pos[drv_idx]

            pickup = req.passenger.pickup
            dest = req.passenger.destination

            d2p = self._manhattan(
                dr,
                dc,
                pickup.row,
                pickup.col
            )

            p2d = self._manhattan(
                pickup.row,
                pickup.col,
                dest.row,
                dest.col
            )

            total = d2p + p2d

            results.append({
                "request": req,
                "driver": drv,
                "driver_to_pickup": d2p,
                "pickup_to_dest": p2d,
                "total_distance": total,
                "trip_cost": total * self.COST_PER_STEP,
                "travel_time": total * self.TIME_PER_STEP,
            })

            drv_pos[drv_idx] = (
                dest.row,
                dest.col
            )

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

            print(
                f"  Driver start pos     : "
                f"({drv.position.row}, {drv.position.col})"
            )

            print(
                f"  Pickup               : "
                f"({req.passenger.pickup.row}, "
                f"{req.passenger.pickup.col})"
            )

            print(
                f"  Destination          : "
                f"({req.passenger.destination.row}, "
                f"{req.passenger.destination.col})"
            )

            print(f"  Driver -> Pickup dist: {r['driver_to_pickup']}")
            print(f"  Pickup -> Dest dist  : {r['pickup_to_dest']}")
            print(f"  Total distance       : {r['total_distance']}")
            print(f"  Trip cost            : ${r['trip_cost']}")
            print(f"  Travel time          : {r['travel_time']} min")

        print("\n" + "=" * 50)
        print(f"  TOTAL SYSTEM DISTANCE : {total_cost}")
        print("=" * 50)

# ─────────────────────────────────────────────────────────────
# TEST 1
# ─────────────────────────────────────────────────────────────

def test_1():

    print("\n" + "=" * 50)
    print("TEST 1 — 2 drivers, 2 requests, obvious match")
    print("=" * 50)

    drivers = [
        Driver("DA", "Alice", "111", "Toyota", 0, 0),
        Driver("DB", "Bob", "222", "Honda", 9, 9),
    ]

    requests = [
        RideRequest(1, Passenger(1, 1, 3, 3)),
        RideRequest(2, Passenger(8, 8, 6, 6)),
    ]

    assigner = DPAssigner(drivers, requests)

    results, total_cost = assigner.assign()

    assigner.display(results, total_cost)


# ─────────────────────────────────────────────────────────────
# TEST 2
# ─────────────────────────────────────────────────────────────

def test_2():

    print("\n" + "=" * 50)
    print("TEST 2 — 1 driver serves 2 chained requests")
    print("=" * 50)

    drivers = [
        Driver("DC", "Carol", "333", "BMW", 0, 0),
    ]

    requests = [
        RideRequest(1, Passenger(2, 0, 5, 0)),
        RideRequest(2, Passenger(6, 0, 9, 0)),
    ]

    assigner = DPAssigner(drivers, requests)

    results, total_cost = assigner.assign()

    assigner.display(results, total_cost)


# ─────────────────────────────────────────────────────────────
# TEST 3
# ─────────────────────────────────────────────────────────────

def test_3():

    print("\n" + "=" * 50)
    print("TEST 3 — 3 drivers, 3 requests")
    print("=" * 50)

    drivers = [
        Driver("D1", "Dan", "444", "Ford", 0, 0),
        Driver("D2", "Eve", "555", "Kia", 5, 0),
        Driver("D3", "Fred", "666", "Audi", 0, 5),
    ]

    requests = [
        RideRequest(1, Passenger(4, 0, 4, 4)),
        RideRequest(2, Passenger(0, 4, 4, 4)),
        RideRequest(3, Passenger(5, 5, 9, 9)),
    ]

    assigner = DPAssigner(drivers, requests)

    results, total_cost = assigner.assign()

    assigner.display(results, total_cost)


# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":

    test_1()
    test_2()
    test_3()

    print("\nAll tests complete.")
