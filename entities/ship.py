from typing import Any

from data_types import vector, rotator # for lib functions
from data_types.vector import Vector2D
from data_types.rotator import Rotator
from data_types.triangle import Triangle
import pygame
from pathlib import Path
import math

# Constants
MAGIC_RADIAN_NUMBER = math.pi/180 # converts degrees to radians when multiplied
MAGIC_DEGREE_NUMBER = 1/(math.pi/180) # converts radians to degrees when multiplied 

class Ship(pygame.sprite.Sprite):
    location: Vector2D
    _rotation: Rotator = 0

    max_health: float
    health: float

    heading: Vector2D = Vector2D(0,1)

    speed: float
    
    color = (0,0,0)
    shape: pygame.Rect
    triangle: Triangle

    def _set_rotation(self, rotation: Rotator):
        self.triangle = self.triangle.rotate(self._rotation - rotation)
        self._rotation = rotation

    def _get_rotation(self) -> Rotator:
        return self._rotation
    
    def add_rotation(self, rotation: Rotator):
        self.rotation += rotation

    def move(self, direction: Vector2D):
        self.rotation = math.atan2(-direction.y, direction.x) * MAGIC_DEGREE_NUMBER
        self.heading = direction

    rotation = property(_get_rotation, _set_rotation)

    def __init__(self, location: Vector2D, rotation: Rotator, max_health: float, speed: float):
        pygame.sprite.Sprite.__init__(self)

        self.location = location
        self.triangle = Triangle(self.location, Vector2D(50, 0), Vector2D(0, 50), Vector2D(0, -50))
        self.rotation = rotation
        self.max_health, self.health = max_health, max_health
        self.speed = speed
        self.color = (0, 255, 0)
        
    
    def update(self, *args: Any, **kwargs: Any) -> None:
        super().update(*args, **kwargs)
        self.location = self.location + (self.heading * self.speed)
        self.triangle.center = self.location

    def draw(self, screen: pygame.Surface):
        shape = pygame.draw.polygon(screen, self.color, [x.tuple for x in self.triangle.tuple])


Ship(Vector2D(0,0), 0, 100, 4)