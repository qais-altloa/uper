# algorithms.py

class CostMatrix:
    def __init__(self, drivers, requests):
        self.drivers = drivers
        self.requests = requests
        # create empty matrix
        self.matrix = []

    # ─────────────────────────────────────────

    def compute(self):
        # loop on every driver
        for driver in self.drivers:
            row = []
            # loop on every request
            for request in self.requests:
                pickup = request.passenger.pickup
                # Manhattan Distance
                cost = abs(driver.position.row - pickup.row) + \
                       abs(driver.position.col - pickup.col)
                row.append(cost)
            self.matrix.append(row)

    # ─────────────────────────────────────────

    def get_cost(self, driver_index, request_index):
        return self.matrix[driver_index][request_index]

    # ─────────────────────────────────────────
    def display(self):
        print("Cost Matrix:\n")
        for row in self.matrix:
            print(row)

    
