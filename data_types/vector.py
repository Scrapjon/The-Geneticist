from math import sin, cos, atan2, radians, sqrt, pi
from dataclasses import dataclass

# Constants
MAGIC_RADIAN_NUMBER = pi/180 # converts degrees to radians when multiplied
MAGIC_DEGREE_NUMBER = 1/(pi/180) # converts radians to degrees when multiplied 

@dataclass
class Vector2D:
    x: float
    y: float
    
    @property
    def tuple(self):
        return self.x, self.y

    
    def __add__(self, rhs):
        if type(rhs) == Vector2D:
            return Vector2D((self.x + rhs.x), (self.y + rhs.y))
        return Vector2D((self.x + rhs), (self.y + rhs))
    
    def __sub__(self, rhs):
        if type(rhs) == Vector2D:
            return Vector2D((self.x - rhs.x), (self.y - rhs.y))
        return Vector2D((self.x - rhs), (self.y - rhs))
    
    def __mul__(self, rhs):
        if type(rhs) == Vector2D:
            return Vector2D((self.x * rhs.x), (self.y * rhs.y))
        return Vector2D((self.x * rhs), (self.y * rhs))
    
    def __truediv__(self, rhs):
        if type(rhs) == Vector2D:
            return Vector2D((self.x / rhs.x), (self.y / rhs.y))
        return Vector2D((self.x / rhs), (self.y / rhs))
    
    def rotate(self, angle: float):
        """
        Returns a rotated vector.
        angle (float): Angle in degrees to rotate the vector by.
        """
        angle = radians(angle)
        s = sin(angle)
        c = cos(angle)
        return Vector2D(
            x = (self.x * c) - (self.y * s),
            y = (self.y * c) + (self.x * s)
        )
    
    def get_angle(self):
        return atan2(self.y, self.x) / (2 * pi)
    
    def dot(self, rhs):
        return dot(self, rhs)
    
    def length(self):
        return length(self)

    def length_sq(self):
        return length_sq(self)
    
    def normalise(self):
        _length = self.length()
        if _length == 0:
            return Vector2D(0,0)
        return self / _length
    
def dot(lhs: Vector2D, rhs: Vector2D) -> float:
    return (lhs.x * rhs.x) + (lhs.y * rhs.y)

def length_sq(vector: Vector2D) -> float:
    x = vector.x**2
    y = vector.y**2
    return x + y

def length(vector: Vector2D) -> float:
    return sqrt(length_sq(vector))



