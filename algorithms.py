# algorithms.py
# Contains all algorithms: BFS, Greedy, Divide & Conquer, DP

import math
from collections import deque
from models import Cell


class BFS:
    """Handles pathfinding using BFS algorithm"""
    
    DIRECTIONS = [(0, 1), (0, -1), (1, 0), (-1, 0)]
    
    @staticmethod
    def find_path(grid, start, end):
        """
        Find shortest path using BFS
        Returns: (distance, path_list)
        """
        N, M = grid.get_size()
        
        if start.row == end.row and start.col == end.col:
            return 0, [start]
        
        parent = {(start.row, start.col): None}
        queue = deque([(start.row, start.col, 0)])
        
        while queue:
            r, c, dist = queue.popleft()
            
            for dr, dc in BFS.DIRECTIONS:
                nr, nc = r + dr, c + dc
                
                if (0 <= nr < N and 0 <= nc < M and 
                    (nr, nc) not in parent and 
                    not grid.is_blocked(nr, nc)):
                    
                    parent[(nr, nc)] = (r, c)
                    
                    if nr == end.row and nc == end.col:
                        # Reconstruct path
                        path = []
                        cur = (end.row, end.col)
                        while cur is not None:
                            path.append(Cell(cur[0], cur[1]))
                            cur = parent[cur]
                        path.reverse()
                        return dist + 1, path
                    
                    queue.append((nr, nc, dist + 1))
        
        return math.inf, []


class GreedySelector:
    """Selects nearest available driver using greedy approach"""
    
    def select(self, drivers, passenger):
        """Choose the closest available driver"""
        best_driver = None
        min_distance = math.inf
        
        for driver in drivers:
            if driver.available:
                distance = driver.position.manhattan_distance(passenger.pickup)
                if distance < min_distance:
                    min_distance = distance
                    best_driver = driver
        
        return best_driver, min_distance


class DivideAndConquer:
    """Divides grid into regions for efficient driver search"""
    
    def __init__(self, grid):
        self.grid = grid
    
    def get_region(self, position, num_regions=4):
        """Determine which region a cell belongs to"""
        rows, cols = self.grid.get_size()
        region_rows = rows // 2
        region_cols = cols // 2
        
        if position.row < region_rows and position.col < region_cols:
            return 0  # Top-left
        elif position.row < region_rows and position.col >= region_cols:
            return 1  # Top-right
        elif position.row >= region_rows and position.col < region_cols:
            return 2  # Bottom-left
        else:
            return 3  # Bottom-right
    
    def find_nearest_in_region(self, drivers, passenger, region):
        """Find nearest driver in specific region"""
        nearest = None
        min_dist = math.inf
        
        for driver in drivers:
            if driver.available and self.get_region(driver.position) == region:
                dist = driver.position.manhattan_distance(passenger.pickup)
                if dist < min_dist:
                    min_dist = dist
                    nearest = driver
        
        return nearest, min_dist
    
    def search(self, drivers, passenger):
        """Search for nearest driver using divide and conquer"""
        passenger_region = self.get_region(passenger.pickup)
        
        # First search in same region
        driver, dist = self.find_nearest_in_region(drivers, passenger, passenger_region)
        
        if driver:
            return driver
        
        # Search in other regions
        best_driver = None
        best_dist = math.inf
        
        for region in range(4):
            if region != passenger_region:
                d, dist = self.find_nearest_in_region(drivers, passenger, region)
                if d and dist < best_dist:
                    best_dist = dist
                    best_driver = d
        
        return best_driver


class DPAssigner:
    """Handles optimal assignment of multiple drivers to multiple requests"""
    
    COST_PER_STEP = 5
    TIME_PER_STEP = 2
    
    def __init__(self, drivers, requests, use_bfs=False, grid=None):
        self.drivers = drivers
        self.requests = requests
        self.use_bfs = use_bfs
        self.grid = grid
        self.R = len(requests)
        self.D = len(drivers)
    
    def _get_path_cost(self, driver_pos, pickup, destination):
        """Get path cost between points"""
        if self.use_bfs and self.grid:
            from algorithms import BFS
            dist1, _ = BFS.find_path(self.grid, driver_pos, pickup)
            dist2, _ = BFS.find_path(self.grid, pickup, destination)
            return dist1 + dist2
        else:
            return (driver_pos.manhattan_distance(pickup) + 
                   pickup.manhattan_distance(destination))
    
    def assign(self):
        """Assign requests to drivers using DP"""
        if self.R == 0 or self.D == 0:
            return [], 0
        
        # DP table and choice tracking
        dp = {}
        choice = {}
        
        dp[0] = 0
        
        for mask in range(1 << self.R):
            if mask not in dp:
                continue
            
            # Find first unassigned request
            next_req = -1
            for r in range(self.R):
                if not (mask >> r & 1):
                    next_req = r
                    break
            
            if next_req == -1:
                continue
            
            # Try assigning to each driver
            for d in range(self.D):
                if not self.drivers[d].available:
                    continue
                
                driver_pos = self.drivers[d].position
                pickup = self.requests[next_req].passenger.pickup
                dest = self.requests[next_req].passenger.destination
                
                cost = self._get_path_cost(driver_pos, pickup, dest)
                
                new_mask = mask | (1 << next_req)
                new_cost = dp[mask] + cost
                
                if new_mask not in dp or new_cost < dp[new_mask]:
                    dp[new_mask] = new_cost
                    choice[new_mask] = (next_req, d)
        
        # Reconstruct assignment
        assignments = []
        if (1 << self.R) - 1 in choice:
            mask = (1 << self.R) - 1
            while mask > 0:
                req_idx, drv_idx = choice[mask]
                assignments.append((req_idx, drv_idx))
                mask ^= (1 << req_idx)
        
        return assignments, dp.get((1 << self.R) - 1, 0)


class IntelligentAlgorithmSelector:
    """Automatically selects the best algorithm based on current situation (silent mode)"""
    
    def __init__(self, grid, drivers, requests):
        self.grid = grid
        self.drivers = drivers
        self.requests = requests
    
    def analyze_situation(self):
        """Analyze current situation and return recommendations"""
        grid_size = self.grid.rows * self.grid.cols
        num_drivers = len([d for d in self.drivers if d.available])
        num_requests = len(self.requests)
        obstacle_density = self.calculate_obstacle_density()
        driver_density = num_drivers / grid_size if grid_size > 0 else 0
        
        # Decision logic for driver selection algorithm
        if num_requests > 2 and num_drivers >= num_requests:
            return {'use_dp': True, 'use_dc': False, 'use_greedy': False}
        
        elif grid_size > 5000 or (self.grid.rows > 30 and self.grid.cols > 30):
            return {'use_dp': False, 'use_dc': True, 'use_greedy': False}
        
        elif obstacle_density > 0.4:
            return {'use_dp': False, 'use_dc': False, 'use_greedy': True}
        
        elif driver_density < 0.05:
            return {'use_dp': False, 'use_dc': True, 'use_greedy': False}
        
        else:
            return {'use_dp': False, 'use_dc': False, 'use_greedy': True}
    
    def calculate_obstacle_density(self):
        """Calculate percentage of blocked cells"""
        blocked = 0
        total = self.grid.rows * self.grid.cols
        for i in range(self.grid.rows):
            for j in range(self.grid.cols):
                if self.grid.is_blocked(i, j):
                    blocked += 1
        return blocked / total if total > 0 else 0
    
    def select_driver(self, passenger, use_dp_assignment=False, all_requests=None):
        """Select driver based on analyzed situation"""
        decision = self.analyze_situation()
        
        if decision['use_dp'] and use_dp_assignment and all_requests:
            return None
        
        elif decision['use_dc']:
            dc = DivideAndConquer(self.grid)
            driver = dc.search(self.drivers, passenger)
            if driver:
                return driver
        
        # Default to GREEDY
        greedy = GreedySelector()
        driver, distance = greedy.select(self.drivers, passenger)
        return driver
    
    def should_use_dp(self):
        """Check if DP should be used"""
        decision = self.analyze_situation()
        return decision['use_dp']
