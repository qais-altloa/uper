class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col

    def __eq__(self, other):
        return self.row == other.row and self.col == other.col

    def __repr__(self):
        return f"Cell({self.row}, {self.col})"

class Driver:
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
    def __init__(self, pickup_row, pickup_col, dest_row, dest_col):
        self.pickup = Cell(pickup_row, pickup_col)
        self.destination = Cell(dest_row, dest_col)

    def __repr__(self):
        return f"Passenger({self.pickup}, {self.destination})"


class RideRequest:
    def __init__(self, id, passenger):
        self.id = id
        self.passenger = passenger

    def __repr__(self):
        return f"RideRequest(id={self.id}, passenger={self.passenger})"
