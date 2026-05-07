# algorithms.py

class CostMatrix:
    def __init__(self, drivers, requests):
        self.drivers = drivers
        self.requests = requests
        self.matrix = []

    # ─────────────────────────────────────────

    def compute(self):
        for driver in self.drivers:
            row = []
            for request in self.requests:
                pickup = request.passenger.pickup
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

    
