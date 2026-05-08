class Cell:
    # Represents a single position (row, col) in the grid
    def __init__(self, row, col):
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
        self.id = id
        self.name = name
        self.phone = phone
        self.car = car
        self.position = Cell(row, col)
        self.available = True

    def __repr__(self):
        return (f"Driver(id={self.id}, name={self.name}, "
                f"phone={self.phone}, car={self.car}, "
                f"position={self.position}, available={self.available})")

class Passenger:
    # Represents a passenger request with pickup and destination
    def __init__(self, pickup_row, pickup_col, dest_row, dest_col):
        self.pickup = Cell(pickup_row, pickup_col)
        self.destination = Cell(dest_row, dest_col)

    def __repr__(self):
        return f"Passenger({self.pickup}, {self.destination})"


class RideRequest:
    # Represents a ride request made by a passenger
    def __init__(self, id, passenger):
        self.id = id    # Unique request ID
        self.passenger = passenger    # store the passenger inside the request

    def __repr__(self):
        return f"RideRequest(id={self.id}, passenger={self.passenger})"
