from math import sin, cos, radians, sqrt
from pathlib import Path
from typing import Any

from pygame import Surface

from data_types.rotator import Rotator
from data_types.vector import Vector2D
from .ship import Ship

class EnemyShip(Ship):
    
    def __init__(self, location: Vector2D, rotation: float, max_health: float, speed: float, world):
        super().__init__(location, rotation, max_health, speed)
        self.color = (255, 0, 0)
        self.world = world

    def draw(self, screen: Surface):
        return super().draw(screen)
    
    def update(self, *args: Any, **kwargs: Any) -> None:
        p_loc = self.world.player.location
        goal_dir = p_loc - self.location
        goal_dir = goal_dir.normalise()
        self.move(goal_dir)
        return super().update(*args, **kwargs)