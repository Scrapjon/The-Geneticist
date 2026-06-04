import math
from pathlib import Path

from data_types.rotator import Rotator
from data_types.vector import Vector2D

from .ship import Ship

class PlayerShip(Ship):
    
    def __init__(self, location: Vector2D, rotation: float, max_health: float, speed: float):
        super().__init__(location, rotation, max_health, speed)