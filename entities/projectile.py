from .entity import Entity
from typing import Any
from data_types import Circle, Vector2D
import pygame

class Projectile(Entity):


    circle: Circle
    velocity: Vector2D # normalised vector for direction
    speed: float
    owner: Entity
    damage: float
    alive: bool

    def __get_radius__(self) -> float:
        return self.circle.radius

    def __set_radius__(self, radius: float):
        self.circle.radius = radius

    radius = property(__get_radius__, __set_radius__)

    def __init__(self, location: Vector2D, radius: float, velocity: Vector2D, owner: Entity, speed: float = 2, damage: float = 0) -> None:
        super().__init__(location)
        self.circle = Circle(location, radius)
        self.speed = speed
        self.velocity = velocity
        self.owner = owner
        self.damage = damage
        self.alive = True

    def update(self, *args: Any, **kwargs: Any) -> None:
        # Deliberately skip Entity.update's edge wrapping. Ships wrap, but a
        # bullet that wraps lives forever and can loop back into whoever fired
        # it, which muddies the damage telemetry. Bullets die at the edge.
        self.location = self.location + (self.velocity * self.speed)
        self.circle.center = self.location

        if "world" in kwargs:
            w = kwargs["world"].screen.get_width()
            h = kwargs["world"].screen.get_height()
            if not (0 <= self.location.x <= w and 0 <= self.location.y <= h):
                self.alive = False

    def draw(self, screen: pygame.Surface):
        # tint player shots so the two damage flows are readable in the demo
        colour = "cyan" if (self.owner is getattr(self, "_player_ref", None)) else "blue"
        pygame.draw.circle(screen, colour, self.location.tuple, self.radius)

    def handle_collision(self, world):
        if not self.alive:
            return

        owner_is_player = (self.owner is world.player)
        self._player_ref = world.player  # only used to pick a draw colour

        for entity in world.entities:
            if entity.entity_type != "Ship":
                continue
            if (entity is self.owner) or (entity is self):
                continue
            if not entity.triangle.is_inside(self.location):
                continue

            target_is_player = (entity is world.player)

            # Player shot landing on an enemy.
            if owner_is_player and not target_is_player:
                entity.take_damage(self.damage)
                self.alive = False
                return

            # Enemy shot landing on the player. Credit the firing enemy and the
            # wave-wide damage total so the fitness denominator has something to
            # divide by.
            if (not owner_is_player) and target_is_player:
                entity.take_damage(self.damage)
                if hasattr(self.owner, "register_hit"):
                    self.owner.register_hit(self.damage)
                world.geneticist.register_player_damage(self.damage)
                self.alive = False
                return

            # Anything else is friendly fire. Let the round keep travelling.
