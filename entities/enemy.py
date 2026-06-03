from math import sin, cos, radians, sqrt
from pathlib import Path
from typing import Any

from pygame import Surface

from data_types.rotator import Rotator
from data_types.vector import Vector2D
from .ship import Ship, DEFAULT_SHIP_ASSET_PATH

class EnemyShip(Ship):

    def __init__(self, location: Vector2D, rotation: float, max_health: float, speed: float, sprite_path: Path = DEFAULT_SHIP_ASSET_PATH):
        super().__init__(location, rotation, max_health, speed, sprite_path)

    def draw(self, screen: Surface):
        return super().draw(screen)
    
    def update(self, *args: Any, **kwargs: Any) -> None:
        
        return super().update(*args, **kwargs)