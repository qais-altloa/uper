# models.py

class Cell:
    def __init__(self, row, col):
        self.row = row
        self.col = col

    def manhattan(self, other):
        return abs(self.row - other.row) + abs(self.col - other.col)

    def __eq__(self, other):
        return self.row == other.row and self.col == other.col

    def __hash__(self):
        return hash((self.row, self.col))

    def __repr__(self):
        return f"({self.row},{self.col})"


class Driver:
    def __init__(self, driver_id, name, row, col):
        self.id = driver_id
        self.name = name
        self.position = Cell(row, col)
        self.available = True
        self.rating = round(__import__('random').uniform(3.0, 5.0), 1)
        self.trips = 0

    def add_rating(self, stars):
        """Update rating as a running average (stars: 1-5)."""
        self.rating = round((self.rating * self.trips + stars) / (self.trips + 1), 1)
        self.trips += 1

    def __repr__(self):
        return f"Driver(D{self.id}, {self.name}, rating={self.rating}, pos={self.position})"


class Request:
    def __init__(self, request_id, pickup_row, pickup_col, dest_row, dest_col):
        self.id = request_id
        self.pickup = Cell(pickup_row, pickup_col)
        self.destination = Cell(dest_row, dest_col)

    def __repr__(self):
        return f"Request(R{self.id}, pickup={self.pickup}, dest={self.destination})"
