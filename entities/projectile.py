from .entity import Entity
from typing import Any
from data_types import Circle, Vector2D
import pygame

class Projectile(Entity):

    
    circle: Circle
    velocity: Vector2D # normalised vector for direction
    speed: float
    owner: Entity
    alive: bool

    def __get_radius__(self) -> float:
        return self.circle.radius
    
    def __set_radius__(self, radius: float):
        self.circle.radius = radius
    
    radius = property(__get_radius__, __set_radius__)
    
    def __init__(self, location: Vector2D, radius: float, velocity: Vector2D, owner: Entity ,speed: float = 5) -> None:
        super().__init__(location)
        self.circle = Circle(location, radius)
        self.speed = speed
        self.velocity = velocity
        self.owner = owner
    
    def update(self, *args: Any, **kwargs: Any) -> None:
        super().update(*args, **kwargs)
        self.location = self.location + (self.velocity * self.speed)
        self.circle.center = self.location
    
    def draw(self, screen: pygame.Surface):
        pygame.draw.circle(screen, "blue", self.location.tuple, self.radius)
    
    def handle_collision(self, world):
        for entity in world.entities:
                if entity.entity_type == "Ship":
                    if (entity is not self.owner) and (entity is not self):
                        if entity.triangle.is_inside(self.location):
                            entity.alive = False
                            self.alive = False
