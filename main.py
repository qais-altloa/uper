# main.py
# Main game class and user interface

import os
import time
import random
import math
from models import Driver, Passenger, RideRequest, Cell
from grid import Grid
from algorithms import BFS, GreedySelector, DivideAndConquer, DPAssigner, IntelligentAlgorithmSelector


class TripManager:
    """Manages individual trips and animations"""
    
    COST_PER_STEP = 5
    TIME_PER_STEP = 2
    
    def __init__(self, grid, bfs_solver):
        self.grid = grid
        self.bfs = bfs_solver
    
    def animate_movement(self, driver, path, purpose):
        """Animate driver movement step by step"""
        print(f"\n🎬 Driver {driver.name} moving to {purpose}...")
        
        for i, step in enumerate(path):
            self.grid.update_driver_position(driver, step)
            self.grid.display(f"Step {i+1}/{len(path)} - Moving to {purpose}")
            time.sleep(0.2)
        
        print(f"✅ Driver {driver.name} reached {purpose}!")


class RideMatcher:
    """Main system that matches drivers with ride requests"""
    
    def __init__(self, grid, drivers):
        self.grid = grid
        self.drivers = drivers
        self.bfs = BFS()
        self.trip_manager = TripManager(grid, self.bfs)
        self.analyzer = IntelligentAlgorithmSelector(self.grid, self.drivers, [])
    
    def process_requests_auto(self, requests):
        """Process requests with automatic algorithm selection (silent mode)"""
        self.analyzer = IntelligentAlgorithmSelector(self.grid, self.drivers, requests)
        
        results = []
        
        # Use DP if recommended and multiple requests
        if self.analyzer.should_use_dp() and len(requests) > 1:
            print("\n🎯 Optimizing multiple requests for best efficiency...")
            results = self.process_multiple_requests_dp(requests)
        else:
            # Process each request individually
            for request in requests:
                result = self.process_single_request_auto(request)
                if result:
                    results.append(result)
        
        return results
    
    def process_single_request_auto(self, request):
        """Process a single request with automatic algorithm selection"""
        passenger = request.passenger
        print(f"\n{'='*60}")
        print(f"🔄 Processing Request {request.id}")
        print(f"   Pickup: {passenger.pickup}")
        print(f"   Destination: {passenger.destination}")
        print(f"{'='*60}")
        
        # Step 1: Automatically select algorithm and find driver
        driver = self.analyzer.select_driver(passenger, use_dp_assignment=False)
        
        if not driver:
            print("❌ No driver available!")
            return None
        
        # Step 2: BFS Path to pickup
        dist_to_pickup, path_to_pickup = self.bfs.find_path(self.grid, driver.position, passenger.pickup)
        
        if dist_to_pickup == math.inf:
            print(f"❌ No path from driver {driver.name} to pickup!")
            return None
        
        # Step 3: Show driver info
        print(f"\n🚗 Assigned Driver:")
        print(f"   Name: {driver.name}")
        print(f"   Car: {driver.car}")
        print(f"   Phone: {driver.phone}")
        print(f"   Current Position: {driver.position}")
        
        # Step 4: Animate driver moving to pickup
        self.trip_manager.animate_movement(driver, path_to_pickup, f"pickup point {passenger.pickup}")
        
        # Step 5: Show trip cost and time to pickup
        cost_to_pickup = dist_to_pickup * self.trip_manager.COST_PER_STEP
        time_to_pickup = dist_to_pickup * self.trip_manager.TIME_PER_STEP
        
        print(f"\n💰 Trip to Pickup:")
        print(f"   Distance: {dist_to_pickup} steps")
        print(f"   Cost: {cost_to_pickup} EGP")
        print(f"   Time: {time_to_pickup} minutes")
        
        # Step 6: Get passenger agreement
        input("\n⏎ Press Enter when passenger agrees to start the ride...")
        
        # Step 7: BFS Path to destination
        dist_to_dest, path_to_dest = self.bfs.find_path(self.grid, passenger.pickup, passenger.destination)
        
        if dist_to_dest == math.inf:
            print(f"❌ No path from pickup to destination!")
            return None
        
        # Step 8: Animate driver moving to destination
        # Clear pickup marker
        self.grid.grid[passenger.pickup.row][passenger.pickup.col] = '0'
        self.trip_manager.animate_movement(driver, path_to_dest, f"destination {passenger.destination}")
        
        # Step 9: Calculate total trip
        total_distance = dist_to_pickup + dist_to_dest
        total_cost = total_distance * self.trip_manager.COST_PER_STEP
        total_time = total_distance * self.trip_manager.TIME_PER_STEP
        
        result = {
            'request': request,
            'driver': driver,
            'dist_to_pickup': dist_to_pickup,
            'dist_to_dest': dist_to_dest,
            'total_distance': total_distance,
            'cost': total_cost,
            'time': total_time
        }
        
        return result
    
    def process_multiple_requests_dp(self, requests):
        """Process multiple requests using DP optimization"""
        assigner = DPAssigner(self.drivers, requests, use_bfs=True, grid=self.grid)
        assignments, total_cost = assigner.assign()
        
        if not assignments:
            print("❌ DP optimization failed! Falling back to individual processing...")
            # Fallback to individual processing
            results = []
            for request in requests:
                result = self.process_single_request_auto(request)
                if result:
                    results.append(result)
            return results
        
        results = []
        for req_idx, drv_idx in assignments:
            request = requests[req_idx]
            driver = self.drivers[drv_idx]
            
            # Process individual trip
            result = self.process_single_request_with_assigned_driver(request, driver)
            if result:
                result['dp_optimized'] = True
                results.append(result)
                driver.available = False
        
        return results
    
    def process_single_request_with_assigned_driver(self, request, driver):
        """Process request with pre-assigned driver"""
        passenger = request.passenger
        
        print(f"\n{'='*60}")
        print(f"🔄 Processing Request {request.id}")
        print(f"   Driver: {driver.name}")
        print(f"   Pickup: {passenger.pickup}")
        print(f"   Destination: {passenger.destination}")
        print(f"{'='*60}")
        
        # BFS Path to pickup
        dist_to_pickup, path_to_pickup = self.bfs.find_path(self.grid, driver.position, passenger.pickup)
        
        if dist_to_pickup == math.inf:
            return None
        
        # Show driver info
        print(f"\n🚗 Driver Details:")
        print(f"   Name: {driver.name}")
        print(f"   Car: {driver.car}")
        print(f"   Phone: {driver.phone}")
        
        # Animate to pickup
        self.trip_manager.animate_movement(driver, path_to_pickup, f"pickup point {passenger.pickup}")
        
        # Show cost to pickup
        cost_to_pickup = dist_to_pickup * self.trip_manager.COST_PER_STEP
        time_to_pickup = dist_to_pickup * self.trip_manager.TIME_PER_STEP
        print(f"\n💰 Cost to pickup: {cost_to_pickup} EGP | Time: {time_to_pickup} min")
        
        input("\n⏎ Press Enter when passenger agrees to start the ride...")
        
        # BFS to destination
        dist_to_dest, path_to_dest = self.bfs.find_path(self.grid, passenger.pickup, passenger.destination)
        
        if dist_to_dest == math.inf:
            return None
        
        # Clear pickup marker
        self.grid.grid[passenger.pickup.row][passenger.pickup.col] = '0'
        
        # Animate to destination
        self.trip_manager.animate_movement(driver, path_to_dest, f"destination {passenger.destination}")
        
        total_distance = dist_to_pickup + dist_to_dest
        total_cost = total_distance * self.trip_manager.COST_PER_STEP
        total_time = total_distance * self.trip_manager.TIME_PER_STEP
        
        result = {
            'request': request,
            'driver': driver,
            'dist_to_pickup': dist_to_pickup,
            'dist_to_dest': dist_to_dest,
            'total_distance': total_distance,
            'cost': total_cost,
            'time': total_time
        }
        
        return result
    
    def generate_report(self, results):
        """Generate final report showing trip details"""
        print("\n" + "="*80)
        print("📋 FINAL TRIP REPORT")
        print("="*80)
        
        total_cost = 0
        total_time = 0
        
        for result in results:
            request = result['request']
            driver = result['driver']
            
            print(f"\n🚕 TRIP {request.id}:")
            print(f"   Driver: {driver.name}")
            print(f"   Vehicle: {driver.car}")
            print(f"   Contact: {driver.phone}")
            print(f"   Distance to pickup: {result['dist_to_pickup']} steps")
            print(f"   Distance to destination: {result['dist_to_dest']} steps")
            print(f"   Total distance: {result['total_distance']} steps")
            print(f"   Cost: {result['cost']} EGP")
            print(f"   Time: {result['time']} minutes")
            
            total_cost += result['cost']
            total_time += result['time']
        
        print("\n" + "="*80)
        print("💰 SUMMARY")
        print("="*80)
        print(f"   Total trips completed: {len(results)}")
        print(f"   Total cost: {total_cost} EGP")
        print(f"   Total time: {total_time} minutes")
        print("="*80)


class UberGame:
    """Main game class handling user interaction"""
    
    def __init__(self):
        self.player_name = ""
        self.grid = None
        self.drivers = []
        self.matcher = None
    
    def clear_screen(self):
        """Clear console screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def print_header(self):
        """Print game header"""
        print("="*60)
        print("   🚕 SMART UBER RIDE MATCHING SYSTEM 🚕")
        print("="*60)
    
    def get_player_name(self):
        """Get player name"""
        self.print_header()
        self.player_name = input("\n👤 Please enter your name: ").strip()
        if not self.player_name:
            self.player_name = "Guest"
        print(f"\n✨ Hello, {self.player_name}! Welcome to the Uber System! ✨")
        input("\n⏎ Press Enter to continue...")
    
    def setup_grid(self):
        """Setup grid with user input"""
        self.clear_screen()
        print("\n🏙️  INITIALIZING CITY GRID 🏙️")
        print("-"*50)
        
        while True:
            try:
                rows = int(input("📏 Enter number of rows (5-20): "))
                cols = int(input("📏 Enter number of columns (5-20): "))
                if 5 <= rows <= 20 and 5 <= cols <= 20:
                    break
                print("❌ Please enter values between 5 and 20!")
            except ValueError:
                print("❌ Please enter valid numbers!")
        
        self.grid = Grid(rows, cols)
        
        # Generate obstacles
        print("\n🏗️  Generating obstacles (30% of grid)...")
        self.grid.generate_obstacles(30)
        
        # Place drivers
        num_drivers = int(input("\n🚗 How many drivers do you want to add? (1-10): "))
        num_drivers = max(1, min(10, num_drivers))
        
        free_positions = self.grid.get_free_positions()
        random.shuffle(free_positions)
        
        names = ["Ahmed", "Sara", "Mohamed", "Fatima", "Omar", "Laila", "Youssef", "Mariam", "Khaled", "Nour"]
        cars = ["Toyota Camry", "Honda Civic", "Hyundai Elantra", "Kia Cerato", "Nissan Sunny", 
                "Tesla Model 3", "BMW 320i", "Mercedes C200", "Audi A4", "Ford Focus"]
        phones = ["0100", "0111", "0122", "0133", "0144", "0155", "0166", "0177", "0188", "0199"]
        
        for i in range(min(num_drivers, len(free_positions))):
            row, col = free_positions[i]
            driver = Driver(
                id=i+1,
                name=names[i % len(names)],
                phone=phones[i % len(phones)] + str(random.randint(1000, 9999)),
                car=cars[i % len(cars)],
                row=row,
                col=col
            )
            self.drivers.append(driver)
            self.grid.place_driver(driver)
        
        print(f"\n✅ Added {len(self.drivers)} drivers to the grid!")
        self.grid.display("Initial City Grid")
        input("\n⏎ Press Enter to continue...")
    
    def create_requests(self):
        """Create ride requests from user"""
        self.clear_screen()
        print("\n📱 PASSENGER REQUESTS 📱")
        print("-"*50)
        
        while True:
            try:
                num_requests = int(input("How many ride requests? (1-5): "))
                if 1 <= num_requests <= 5:
                    break
                print("❌ Please enter between 1 and 5!")
            except ValueError:
                print("❌ Please enter a valid number!")
        
        requests = []
        
        for i in range(num_requests):
            print(f"\n{'='*40}")
            print(f"📞 REQUEST {i+1}:")
            print(f"{'='*40}")
            
            while True:
                try:
                    print("\n📍 Pickup location:")
                    pickup_row = int(input("   Row: "))
                    pickup_col = int(input("   Column: "))
                    
                    print("\n🏁 Destination:")
                    dest_row = int(input("   Row: "))
                    dest_col = int(input("   Column: "))
                    
                    if (0 <= pickup_row < self.grid.rows and 0 <= pickup_col < self.grid.cols and
                        0 <= dest_row < self.grid.rows and 0 <= dest_col < self.grid.cols):
                        
                        if not self.grid.is_blocked(pickup_row, pickup_col) and not self.grid.is_blocked(dest_row, dest_col):
                            break
                        else:
                            print("❌ Location cannot be on blocked cells (X)!")
                    else:
                        print(f"❌ Positions must be between 0-{self.grid.rows-1} rows and 0-{self.grid.cols-1} columns!")
                except ValueError:
                    print("❌ Please enter valid numbers!")
            
            passenger = Passenger(pickup_row, pickup_col, dest_row, dest_col)
            request = RideRequest(i+1, passenger)
            requests.append(request)
            
            # Display on grid temporarily
            self.grid.place_passenger(passenger)
            self.grid.place_destination(passenger)
        
        self.grid.display("Grid with all requests")
        input("\n⏎ Press Enter to continue...")
        
        return requests
    
    def process_requests(self, requests):
        """Process ride requests with automatic algorithm selection"""
        self.clear_screen()
        print("\n🚀 PROCESSING RIDE REQUESTS 🚀")
        print("-"*50)
        
        self.matcher = RideMatcher(self.grid, self.drivers)
        results = self.matcher.process_requests_auto(requests)
        
        return results
    
    def play_again(self):
        """Ask if user wants to play again"""
        print("\n" + "="*60)
        play = input("🎮 Do you want to play another round? (yes/no): ").strip().lower()
        return play in ['yes', 'y']
    
    def run(self):
        """Main game loop"""
        self.get_player_name()
        
        playing = True
        while playing:
            self.setup_grid()
            requests = self.create_requests()
            results = self.process_requests(requests)
            
            if results:
                self.matcher.generate_report(results)
            else:
                print("\n❌ No trips were completed successfully!")
            
            playing = self.play_again()
            if playing:
                # Reset for new game
                self.drivers = []
                self.grid = None
                self.matcher = None
        
        print("\n" + "="*60)
        print(f"👋 Thank you for using the Uber System, {self.player_name}! Goodbye! 👋")
        print("="*60)


# ============================================
# MAIN EXECUTION
# ============================================

if __name__ == "__main__":
    game = UberGame()
    game.run()
