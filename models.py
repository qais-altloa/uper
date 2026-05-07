# models.py
# Data classes for Driver and RideRequest

class Driver:
   

class RideRequest:
   

class Cell:
    def __init__(self, row, col):
      self.row=row
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
        return f"Driver({self.id}, {self.name},{self.phone},{self.car},{self.position},{self.available})"       
class Passenger:
  def __init__(self, pickup_row, pickup_col, dest_row, dest_col):
    self.pickup = Cell(pickup_row, pickup_col)
    self.destination = Cell(dest_row, dest_col)
  def __repr__(self):
        return f"Passenger({self.pickup},{self.destination})"
