from typing import Any, Literal

from data_types import Vector2D
import pygame

class Entity(pygame.sprite.Sprite):
    location: Vector2D
    entity_type: Literal["", "Ship"] = "" # stupid bandaid

    def __init__(self, location: Vector2D) -> None:
        pygame.sprite.Sprite.__init__(self)
        self.location = location

    def update(self, *args: Any, **kwargs: Any) -> None:
        if "world" in kwargs.keys():
            world = kwargs['world']
            pad = 0
            if (self.location.x > (width := world.screen.get_width())):
                self.location.x = (self.location.x % width) + pad
            if self.location.x < 0:
                self.location.x = width - pad # it's so strange how variables are function scoped in python...
            if self.location.y > (height := world.screen.get_height()):
                self.location.y = (self.location.y % height) + pad
            if self.location.y < 0:
                self.location.y = height - pad 
                
        return super().update(*args, **kwargs)
    
    def draw(self, screen: pygame.Surface): ...

    def handle_collision(self, world): ...
