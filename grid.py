# grid.py
# Grid management and visualization

import random


class Grid:
    """Represents the city grid"""
    
    def __init__(self, rows, cols):
        self.rows = rows
        self.cols = cols
        self.grid = [['0' for _ in range(cols)] for _ in range(rows)]
        self.drivers = []
    
    def get_size(self):
        return self.rows, self.cols
    
    def is_blocked(self, row, col):
        return self.grid[row][col] == 'X'
    
    def generate_obstacles(self, percentage=30):
        """Generate obstacles randomly"""
        total_cells = self.rows * self.cols
        num_obstacles = int(total_cells * percentage / 100)
        
        obstacles_placed = 0
        while obstacles_placed < num_obstacles:
            row = random.randint(0, self.rows - 1)
            col = random.randint(0, self.cols - 1)
            if self.grid[row][col] == '0':
                self.grid[row][col] = 'X'
                obstacles_placed += 1
    
    def place_driver(self, driver):
        """Place a driver on the grid"""
        self.drivers.append(driver)
        self.grid[driver.position.row][driver.position.col] = f'D{driver.id}'
    
    def place_passenger(self, passenger):
        """Place passenger pickup point"""
        self.grid[passenger.pickup.row][passenger.pickup.col] = 'P'
    
    def place_destination(self, passenger):
        """Place destination point"""
        self.grid[passenger.destination.row][passenger.destination.col] = 'R'
    
    def clear_cell(self, row, col):
        """Clear a cell"""
        if self.grid[row][col] not in ['X', 'R', 'P']:
            self.grid[row][col] = '0'
    
    def update_driver_position(self, driver, new_position):
        """Update driver position on grid"""
        # Clear old position if not occupied by special markers
        if self.grid[driver.position.row][driver.position.col] in [f'D{driver.id}', f'D{driver.id}']:
            self.grid[driver.position.row][driver.position.col] = '0'
        
        driver.position = new_position
        self.grid[new_position.row][new_position.col] = f'D{driver.id}'
    
    def display(self, step_info=""):
        """Display the grid"""
        print("\n" + "=" * (self.cols * 4 + 10))
        if step_info:
            print(f"  {step_info}")
            print("=" * (self.cols * 4 + 10))
        
        # Column numbers
        print("    ", end="")
        for j in range(self.cols):
            print(f"{j:3}", end="")
        print("\n")
        
        for i in range(self.rows):
            print(f"{i:3} ", end="")
            for j in range(self.cols):
                cell = self.grid[i][j]
                if cell == '0':
                    print("  ·", end="")
                elif cell == 'X':
                    print("  █", end="")
                elif cell == 'P':
                    print("  🚩", end="")
                elif cell == 'R':
                    print("  🏁", end="")
                elif cell.startswith('D'):
                    print(f"  D", end="")
                else:
                    print(f"  {cell}", end="")
            print()
        print("=" * (self.cols * 4 + 10))
    
    def get_free_positions(self):
        """Get all free positions for placing drivers"""
        free = []
        for i in range(self.rows):
            for j in range(self.cols):
                if self.grid[i][j] == '0':
                    free.append((i, j))
        return free
