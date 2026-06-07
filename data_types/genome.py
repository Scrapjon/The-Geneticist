from dataclasses import dataclass
from typing import NamedTuple
from .vector import Vector2D

@dataclass
class BoidData:
    separation: float
    alignment: float
    cohesion: float

class Genome(NamedTuple):
    # Boids stuff
    separation: float
    alignment: float
    cohesion: float
    
    # Point-buy mods
    max_health: float
    max_speed: float
    flee_threshold: float
    damage: float

    @property
    def boid_data(self) -> BoidData:
        return BoidData(self.separation, self.alignment, self.cohesion)
