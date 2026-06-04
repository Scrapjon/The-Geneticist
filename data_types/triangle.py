from .vector import Vector2D

class Triangle:
    """
    Triangle data class to store points
    center (Vector2D): World space center of triangle.
    p1 (Vector2D): Local space front point
    p2 (Vector2D): Local space left point
    p3 (Vector2D): Local space right point
    """
    center: Vector2D
    p1: Vector2D
    p2: Vector2D
    p3: Vector2D
    
    def __init__(
        self, 
        center: Vector2D, 
        p1: Vector2D, 
        p2: Vector2D,
        p3: Vector2D):
            self.center = center
            self.p1 = p1
            self.p2 = p2
            self.p3 = p3
        
    def rotate(self, angle: float):
        return Triangle(
            center = self.center,
            p1 = self.p1.rotate(angle),
            p2 = self.p2.rotate(angle),
            p3 = self.p3.rotate(angle)
            )
    
    @property
    def tuple(self) -> tuple[Vector2D, Vector2D, Vector2D]:
        """
        Returns world space coordinates for the three triangle points (p1, p2, p3)
        """
        return (self.p1 + self.center), (self.p2 + self.center), (self.p3 + self.center)
    
    @property
    def area(self) -> float:
        """Area of the triangle using Heron's formula"""
        x1, y1 = self.p1.x, self.p1.y
        x2, y2 = self.p2.x, self.p2.y
        x3, y3 = self.p3.x, self.p3.y
        return abs((x2-x1)*(y3-y1) - (x3-x1)*(y2-y1))
    
    def is_inside(self, point: Vector2D) -> bool:
        area_orig = self.area

        x1, y1 = self.p1.x, self.p1.y
        x2, y2 = self.p2.x, self.p2.y
        x3, y3 = self.p3.x, self.p3.y

        px, py = point.x, point.y

        area1 = abs((x1 - px)*(y2 - py) - (x2 - px)*(y1 - py))
        area2 = abs((x2 - px)*(y3 - py) - (x3 - px)*(y2 - py))
        area3 = abs((x3 - px)*(y1 - py) - (x1 - px)*(y3 - py))

        return (area1 + area2 + area3) == area_orig
        
    
    def __str__(self):
        return f"Triangle(center={self.center}, p1={self.p1}, p2={self.p2}, p3={self.p3})"
        
    def __repr__(self):
        return str(self)