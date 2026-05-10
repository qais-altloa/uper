# models.py
# Data models: Cell, Driver, Passenger, RideRequest
 
 
class Cell:
    # Represents a single position (row, col) in the grid
    def __init__(self, row, col):
        if not isinstance(row, int) or not isinstance(col, int):
            raise ValueError(f"Cell row and col must be integers, got ({row}, {col})")
        if row < 0 or col < 0:
            raise ValueError(f"Cell row and col must be non-negative, got ({row}, {col})")
        self.row = row
        self.col = col
 
    # Compare two cells based on their coordinates
    def __eq__(self, other):
        return self.row == other.row and self.col == other.col
 
    def __repr__(self):
        return f"Cell({self.row}, {self.col})"
 
 
class Driver:
    # Represents a driver in the system
    def __init__(self, id, name, phone, car, row, col):
        if not str(id).strip():
            raise ValueError("Driver id cannot be empty")
        if not str(name).strip():
            raise ValueError("Driver name cannot be empty")
        self.id = id
        self.name = name
        self.phone = phone
        self.car = car
        self.position = Cell(row, col)   # Cell validates row/col
        self.available = True
 
    def __repr__(self):
        return (f"Driver(id={self.id}, name={self.name}, "
                f"phone={self.phone}, car={self.car}, "
                f"position={self.position}, available={self.available})")
 
 
class Passenger:
    # Represents a passenger request with pickup and destination
    def __init__(self, pickup_row, pickup_col, dest_row, dest_col):
        self.pickup      = Cell(pickup_row, pickup_col)   # Cell validates
        self.destination = Cell(dest_row, dest_col)
        if self.pickup == self.destination:
            raise ValueError("Pickup and destination cannot be the same cell")
 
    def __repr__(self):
        return f"Passenger({self.pickup}, {self.destination})"
 
 
class RideRequest:
    # Represents a ride request made by a passenger
    def __init__(self, id, passenger):
        if passenger is None:
            raise ValueError("RideRequest must have a passenger")
        self.id = id
        self.passenger = passenger
 
    def __repr__(self):
        return f"RideRequest(id={self.id}, passenger={self.passenger})"
    def __repr__(self):
        return f"RideRequest(id={self.id}, passenger={self.passenger})"
