from dataclasses import dataclass
from typing import Any, NamedTuple
from .vector import Vector2D

@dataclass
class BoidData:
    separation: float
    alignment: float
    cohesion: float

    def __iter__(self):
        yield self.separation
        yield self.alignment
        yield self.cohesion

@dataclass
class PointBuy:
    # Point-buy mods
    max_health: float
    max_speed: float
    flee_threshold: float
    damage: float

    def __iter__(self):
        yield self.max_health
        yield self.max_speed
        yield self.flee_threshold
        yield self.damage

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
    
    @property
    def point_buy(self) -> PointBuy:
        return PointBuy(self.max_health, self.max_speed, self.flee_threshold, self.damage)
    
    def __len__(self) -> int:
        return len(list(self))

EMPTY_GENOME = Genome(0,0,0,0,0,0,0)