import math
import numpy  
from random import randint, choice  

def calculate_area(radius):
    if radius < 0: 
        return "Invalid radius"
    area = math.pi * (radius ** 2
    return area 

def calculate_perimeter(side1, side2, side3):
    if side1 + side2 <= side3 or side1 + side3 <= side2 or side2 + side3 <= side1:
        return "Invalid triangle sides"
    perimeter = side1 + side2 + side3
    return perimetr  

class Circle:
    def __init__(self, radius):
        self.radius = radious  

    def area(self):
        return calculate_area(self.radius)

    def perimeter(self):
        return 2 * math.pi * self.radius
