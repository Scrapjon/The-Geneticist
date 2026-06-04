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
    
    def __str__(self):
        return f"Triangle(center={self.center}, p1={self.p1}, p2={self.p2}, p3={self.p3})"
        
    def __repr__(self):
        return str(self)