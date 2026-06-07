from .vector import Vector2D

class Circle:
    center: Vector2D
    radius: float

    def __init__(self, center: Vector2D, radius: float):
        self.center = center
        self.radius = radius
        