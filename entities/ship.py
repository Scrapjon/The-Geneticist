from typing import Any
from .entity import Entity
from .projectile import Projectile
from data_types import vector, rotator # for lib functions
from data_types.vector import Vector2D, MAGIC_DEGREE_NUMBER
from data_types.rotator import Rotator
from data_types.triangle import Triangle
import pygame
from pathlib import Path
import math


class Ship(Entity):
    location: Vector2D
    _rotation: Rotator = 0

    max_health: float
    health: float

    velocity: Vector2D = Vector2D(0,1)
    
    color = (0,0,0)
    shape: pygame.Rect
    triangle: Triangle

    alive: bool = True

    def _set_rotation(self, rotation: Rotator):
        self.triangle = self.triangle.rotate(self._rotation - rotation)
        self._rotation = rotation

    def _get_rotation(self) -> Rotator:
        return self._rotation
    
    def add_rotation(self, rotation: Rotator):
        self.rotation += rotation

    def move(self, direction: Vector2D):
        self.rotation = math.atan2(-direction.y, direction.x) * MAGIC_DEGREE_NUMBER
        self.velocity = direction

    rotation = property(_get_rotation, _set_rotation)
    
    def __init__(self, location: Vector2D, rotation: Rotator, max_health: float):
        super().__init__(location)
        self.triangle = Triangle(self.location, Vector2D(50, 0), Vector2D(0, 20), Vector2D(0, -20))
        self.rotation = rotation
        self.max_health, self.health = max_health, max_health
        self.color = (0, 255, 0)
        self.entity_type = "Ship"
        
    
    def update(self, *args: Any, **kwargs: Any) -> None:
        super().update(*args, **kwargs)
        self.location = self.location + (self.velocity)
        self.triangle.center = self.location

    def draw(self, screen: pygame.Surface):
        shape = pygame.draw.polygon(screen, self.color, [x.tuple for x in self.triangle.tuple])

    def shoot(self, world):
        world.spawn_projectile(Projectile(self.location, 10, self.velocity, self))
    
    def handle_collision(self, world):
        pass
        