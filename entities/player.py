from math import atan2

import config
from data_types.vector import Vector2D, MAGIC_DEGREE_NUMBER

from .ship import Ship
from .projectile import Projectile


class PlayerShip(Ship):

    speed: float
    _fire_cooldown: float = 0.0

    # dash state
    _dash_timer: float = 0.0      # time left in the current burst
    _dash_cooldown: float = 0.0   # time left before another dash is allowed
    _dash_dir: Vector2D = None

    def __init__(self, location: Vector2D, rotation: float, max_health: float, speed: float):
        super().__init__(location, rotation, max_health)
        self.speed = speed
        self._dash_dir = Vector2D(1, 0)

    def move(self, direction: Vector2D):
        # WASD only sets where we drift. Facing is the mouse's job now, so unlike
        # the base Ship.move this deliberately leaves rotation alone instead of
        # spinning the ship to point where it's moving.
        self.velocity = direction.normalise() * self.speed

    def dash(self):
        # A committed burst in whatever direction we're already heading. It locks
        # to that heading for its duration so it reads as a deliberate dodge
        # rather than a twitchy teleport, and it's on a cooldown so it can't be
        # spammed to just permanently fly around at dash speed.
        if self._dash_cooldown > 0 or self._dash_timer > 0:
            return
        self._dash_dir = self.velocity.normalise()
        if self._dash_dir.length() == 0:
            self._dash_dir = Vector2D(1, 0)
        self._dash_timer = config.DASH_DURATION
        self._dash_cooldown = config.DASH_COOLDOWN

    @property
    def dash_ready(self) -> bool:
        return self._dash_cooldown <= 0 and self._dash_timer <= 0

    def shoot(self, world, target: Vector2D):
        # Fire toward the cursor instead of along the velocity, so you can kite
        # and shoot in different directions at the same time. Still gated by the
        # cooldown so a held button doesn't spawn a bullet every frame.
        if self._fire_cooldown > 0:
            return
        self._fire_cooldown = config.PLAYER_FIRE_COOLDOWN
        direction = (target - self.location).normalise()
        if direction.length() == 0:
            direction = Vector2D(1, 0)
        world.spawn_projectile(
            Projectile(self.location, 10, direction, self, damage=config.PLAYER_DAMAGE)
        )

    def _face(self, aim: Vector2D):
        aim_dir = aim - self.location
        if aim_dir.length() > 0:
            self.rotation = atan2(-aim_dir.y, aim_dir.x) * MAGIC_DEGREE_NUMBER

    def update(self, *args, **kwargs):
        dt = 1.0 / config.FPS

        if self._fire_cooldown > 0:
            self._fire_cooldown -= dt
        if self._dash_cooldown > 0:
            self._dash_cooldown -= dt

        if self._dash_timer > 0:
            self._dash_timer -= dt
            # Override velocity for the burst, then settle back to normal cruise
            # in the same direction once it ends so you don't lurch to a stop.
            if self._dash_timer <= 0:
                self.velocity = self._dash_dir * self.speed
            else:
                self.velocity = self._dash_dir * (self.speed * config.DASH_SPEED_MULT)

        # Point the ship at the cursor every frame.
        world = kwargs.get("world")
        if world is not None and getattr(world, "aim", None) is not None:
            self._face(world.aim)

        super().update(*args, **kwargs)
