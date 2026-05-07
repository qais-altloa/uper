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
       
