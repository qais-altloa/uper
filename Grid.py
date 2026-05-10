# grid.py
# Grid class: manages the 2D map, placing drivers, passengers, and obstacles
 
 
class Grid:
    def __init__(self, row, col):
        if row <= 0 or col <= 0:
            raise ValueError(f"Grid dimensions must be positive, got ({row}, {col})")
        self.row  = row
        self.col  = col
        self.grid = [[0 for j in range(col)] for i in range(row)]
 
    def _check_bounds(self, row, col, label="Position"):
        """Raise if (row, col) is outside the grid — used before every placement."""
        if not (0 <= row < self.row and 0 <= col < self.col):
            raise ValueError(
                f"{label} ({row}, {col}) is out of grid bounds ({self.row}x{self.col})"
            )
 
    def placeRideRequest(self, passenger):
        self._check_bounds(passenger.pickup.row, passenger.pickup.col, "Pickup")
        self.grid[passenger.pickup.row][passenger.pickup.col] = 'P'
 
    def placeDestination(self, passenger):
        self._check_bounds(passenger.destination.row, passenger.destination.col, "Destination")
        self.grid[passenger.destination.row][passenger.destination.col] = 'R'
 
    def placeDriver(self, driver):
        self._check_bounds(driver.position.row, driver.position.col, "Driver position")
        self.grid[driver.position.row][driver.position.col] = driver.id
 
    def placeObstacle(self, row, col):
        self._check_bounds(row, col, "Obstacle")
        self.grid[row][col] = 'X'
 
    def isValid(self, row, col):
        # Check if position is inside grid bounds and not an obstacle
        if 0 <= row < self.row and 0 <= col < self.col and self.grid[row][col] != 'X':
            return True
        return False
 
    def display(self):
        for i in range(self.row):
            for j in range(self.col):
                print(self.grid[i][j], end=" ")
            print()
