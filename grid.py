# grid.py

import random


class Grid:
    """Represents the city as a 2D grid."""

    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = [['0' for _ in range(cols)] for _ in range(rows)]

    # ── helpers ──────────────────────────────────────────────────────────────

    def get_size(self):
        return self.rows, self.cols

    def is_blocked(self, row, col):
        return self.grid[row][col] == 'X'

    def in_bounds(self, row, col):
        return 0 <= row < self.rows and 0 <= col < self.cols

    def get_free_positions(self):
        return [(r, c) for r in range(self.rows)
                       for c in range(self.cols)
                       if self.grid[r][c] == '0']

    # ── placement ────────────────────────────────────────────────────────────

def generate_obstacles(self, percentage=30):
    total = self.rows * self.cols
    num_obs = int(total * percentage / 100)
    placed = 0
    
    while placed < num_obs:
        r = random.randint(0, self.rows - 1)
        c = random.randint(0, self.cols - 1)
        if self.grid[r][c] == '0':
            self.grid[r][c] = 'X'
            placed += 1

  

    def place_driver(self, driver):
        self.grid[driver.position.row][driver.position.col] = f'D{driver.id}'

    def place_passenger(self, passenger):
        self.grid[passenger.pickup.row][passenger.pickup.col] = 'P'

    def place_destination(self, passenger):
        self.grid[passenger.destination.row][passenger.destination.col] = 'R'

    def clear_cell(self, row, col):
        if self.grid[row][col] not in ('X', 'R', 'P'):
            self.grid[row][col] = '0'

    def update_driver_position(self, driver, new_pos):
        old = driver.position
        if self.grid[old.row][old.col] == f'D{driver.id}':
            self.grid[old.row][old.col] = '0'
        driver.position = new_pos
        self.grid[new_pos.row][new_pos.col] = f'D{driver.id}'

    # ── display ──────────────────────────────────────────────────────────────

    def display(self, title=""):
        width = self.cols * 4 + 10
        print("\n" + "=" * width)
        if title:
            print(f"  {title}")
            print("=" * width)

        # column numbers
        print("    ", end="")
        for j in range(self.cols):
            print(f"{j:3}", end="")
        print("\n")

        for i in range(self.rows):
            print(f"{i:3} ", end="")
            for j in range(self.cols):
                cell = self.grid[i][j]
                if   cell == '0':           print("  ·", end="")
                elif cell == 'X':           print("  █", end="")
                elif cell == 'P':           print("  P", end="")
                elif cell == 'R':           print("  R", end="")
                elif cell.startswith('D'):  print("  D", end="")
                else:                       print(f"  {cell}", end="")
            print()
        print("=" * width)
