from typing import Any

from data_types import vector, rotator # for lib functions
from data_types.vector import Vector2D
from data_types.rotator import Rotator
import pygame
from pathlib import Path
import math

# Constants
DEFAULT_SHIP_ASSET_PATH = Path("assets", "Ship.png")
MAGIC_RADIAN_NUMBER = math.pi/180 # converts degrees to radians when multiplied
MAGIC_DEGREE_NUMBER = 1/(math.pi/180) # converts radians to degrees when multiplied 

class Ship(pygame.sprite.Sprite):
    location: Vector2D
    _rotation: Rotator = 0

    max_health: float
    health: float

    heading: Vector2D = Vector2D(0,1)

    speed: float
 
    image: pygame.Surface


    def _set_rotation(self, rotation: Rotator):
        self.image = pygame.transform.rotate(self.image, self._rotation - rotation)
        self._rotation = rotation

    def _get_rotation(self) -> Rotator:
        return self._rotation
    
    def add_rotation(self, rotation: Rotator):
        self.rotation += rotation

    def move(self, direction: Vector2D):
        direction.y = -direction.y # y axis was inverse of what i wanted it to be?
        self.rotation = math.atan2(direction.y, direction.x) * MAGIC_DEGREE_NUMBER
        self.heading = direction

    rotation = property(_get_rotation, _set_rotation)

    def __init__(self, location: Vector2D, rotation: Rotator, max_health: float, speed: float, sprite_path: Path = DEFAULT_SHIP_ASSET_PATH):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(sprite_path)

        self.location = location
        self.rotation = rotation
        self.max_health, self.health = max_health, max_health
        self.speed = speed
        
    
    def update(self, *args: Any, **kwargs: Any) -> None:
        super().update(*args, **kwargs)
        self.location = self.location + (self.heading * self.speed)

    def draw(self, screen: pygame.Surface):
        screen.blit(self.image, self.location.tuple)


Ship(Vector2D(0,0), 0, 100, 4)