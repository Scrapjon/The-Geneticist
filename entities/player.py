import math
from pathlib import Path

from data_types.rotator import Rotator
from data_types.vector import Vector2D

from .ship import Ship, DEFAULT_SHIP_ASSET_PATH

class PlayerShip(Ship):
    
    def __init__(self, location: Vector2D, rotation: float, max_health: float, speed: float, sprite_path: Path = DEFAULT_SHIP_ASSET_PATH):
        super().__init__(location, rotation, max_health, speed, sprite_path)