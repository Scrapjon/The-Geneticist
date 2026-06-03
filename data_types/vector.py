from dataclasses import dataclass
from math import sqrt

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
    
    def __mul__(self, rhs):
        if type(rhs) == Vector2D:
            return Vector2D((self.x * rhs.x), (self.y * rhs.y))
        return Vector2D((self.x * rhs), (self.y * rhs))

def dot(lhs: Vector2D, rhs: Vector2D) -> float:
    return (lhs.x * rhs.x) + (lhs.y * rhs.y)

def length_squared(vector: Vector2D) -> float:
    x = vector.x**2
    y = vector.y**2
    return x + y

def length(vector: Vector2D) -> float:
    return sqrt(length_squared(vector))



