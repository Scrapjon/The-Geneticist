from enum import IntEnum
from typing import Any, Optional

from pygame import Surface

import config
from data_types import Vector2D, BoidData, Genome
from data_types.genome import normalise_point_buy

from .ship import Ship
from .projectile import Projectile


class EnemyState(IntEnum):
    """
    The genome-driven FSM from the plan. The transitions are all threshold based:
    distance to the player picks PATROL / CHASE / ATTACK, and the flee_threshold
    gene overrides everything once an agent is hurt badly enough.
    """
    PATROL = 0   # too far to care, just flock with the swarm
    CHASE = 1    # player spotted, seek toward them
    ATTACK = 2   # in range, seek AND fire
    FLEE = 3     # health below the flee gene, run away


# colour per state so the FSM is legible on screen during the demo
STATE_COLOURS = {
    EnemyState.PATROL: (150, 150, 150),
    EnemyState.CHASE:  (255, 120, 0),
    EnemyState.ATTACK: (255, 0, 0),
    EnemyState.FLEE:   (0, 160, 255),
}


class EnemyShip(Ship):

    genome: Genome

    def __init__(self, location: Vector2D, rotation: float, world, genome: Genome, difficulty: float = 1.0):
        # Decode the phenotype before handing the resolved health up to Ship,
        # since max_health is no longer a fixed number passed in from main.
        self.genome = normalise_point_buy(genome)
        self.difficulty = difficulty
        self._decode_phenotype()

        super().__init__(location, rotation, self.max_health)

        self.world = world
        self.state = EnemyState.PATROL

        # fitness telemetry
        self.damage_dealt: float = 0.0
        self.spawn_time: float = 0.0
        self.death_time: Optional[float] = None

        self._fire_cooldown: float = 0.0

    def _decode_phenotype(self):
        """
        Turn the four normalised point-buy fractions into concrete stats. The
        combat stats (health, damage) get scaled by the wave difficulty so the
        curve climbs; speed is left unscaled so late waves never outrun the
        player outright, and flee_threshold maps straight to an HP ratio because
        it is a switch, not a 'bigger is stronger' stat (this is the deliberate
        deviation written up in the post-mortem).
        """
        pb = self.genome.point_buy
        self.max_health = config.HEALTH_BASE + config.HEALTH_BUDGET * pb.max_health * self.difficulty
        self.max_speed = config.SPEED_BASE + config.SPEED_BUDGET * pb.max_speed
        self.damage = config.DAMAGE_BASE + config.DAMAGE_BUDGET * pb.damage * self.difficulty
        self.flee_ratio = config.FLEE_MIN + (config.FLEE_MAX - config.FLEE_MIN) * pb.flee_threshold

    @property
    def boid_data(self):
        return BoidData(self.genome.separation, self.genome.alignment, self.genome.cohesion)

    def register_hit(self, amount: float):
        """Called by a projectile of ours that connected with the player."""
        self.damage_dealt += amount

    def draw(self, screen: Surface):
        self.color = STATE_COLOURS[self.state]
        return super().draw(screen)

    def update(self, *args: Any, **kwargs: Any) -> None:
        dt = 1.0 / config.FPS
        if self._fire_cooldown > 0:
            self._fire_cooldown -= dt

        self._update_state()
        self.advance()

        if self.state == EnemyState.ATTACK and self._fire_cooldown <= 0:
            self._fire_at_player()
            self._fire_cooldown = config.ENEMY_FIRE_COOLDOWN

        return super().update(*args, **kwargs)

    # ----- FSM -----

    def _update_state(self):
        player = self.world.player
        dist = (player.location - self.location).length()

        if self.health_ratio < self.flee_ratio:
            self.state = EnemyState.FLEE
        elif dist <= config.ENEMY_ATTACK_RANGE:
            self.state = EnemyState.ATTACK
        elif dist <= config.ENEMY_DETECT_RANGE:
            self.state = EnemyState.CHASE
        else:
            self.state = EnemyState.PATROL

    def _player_direction(self) -> Vector2D:
        return (self.world.player.location - self.location).normalise()

    def _fire_at_player(self):
        direction = self._player_direction()
        self.world.spawn_projectile(
            Projectile(self.location, 8, direction, self, damage=self.damage)
        )

    # ----- steering -----

    def move(self, direction: Vector2D):
        min_speed = 1
        speed = direction.length()
        normalised_dir = direction.normalise()
        if speed > self.max_speed:
            direction = normalised_dir * self.max_speed
        if speed < min_speed:
            direction = normalised_dir * min_speed

        return super().move(direction)

    def _neighbours(self, distance: float):
        # Exclude self this time. The old version left self in the list as a
        # band-aid against dividing by zero; guarding the empty case directly
        # is the cleaner fix flagged in the post-mortem.
        out = []
        for other in self.world.enemies:
            if other is self:
                continue
            if (other.location - self.location).length_sq() < distance * distance:
                out.append(other)
        return out

    def flock(self, distance, power) -> Vector2D:
        neighbours = self._neighbours(distance)
        if not neighbours:
            return Vector2D(0, 0)
        mean_x = sum(n.location.x for n in neighbours) / len(neighbours)
        mean_y = sum(n.location.y for n in neighbours) / len(neighbours)
        return Vector2D((mean_x - self.location.x) * power, (mean_y - self.location.y) * power)

    def align(self, distance: float, power: float):
        neighbours = self._neighbours(distance)
        if not neighbours:
            return Vector2D(0, 0)
        mean_vx = sum(n.velocity.x for n in neighbours) / len(neighbours)
        mean_vy = sum(n.velocity.y for n in neighbours) / len(neighbours)
        return Vector2D((mean_vx - self.velocity.x) * power, (mean_vy - self.velocity.y) * power)

    def avoid(self, distance: float, power: float):
        neighbours = self._neighbours(distance)
        sum_x, sum_y = 0.0, 0.0
        for n in neighbours:
            closeness = distance - (self.location - n.location).length()
            sum_x += (self.location.x - n.location.x) * closeness
            sum_y += (self.location.y - n.location.y) * closeness
        return Vector2D(sum_x * power, sum_y * power)

    def _target_vector(self) -> Vector2D:
        """The seek/flee layer the FSM state decides on, on top of the boids."""
        if self.state in (EnemyState.CHASE, EnemyState.ATTACK):
            return self._player_direction() * config.CHASE_POWER
        if self.state == EnemyState.FLEE:
            return self._player_direction() * (-config.FLEE_POWER)
        return Vector2D(0, 0)

    def advance(self):
        separation, alignment, cohesion = self.boid_data
        flock_vel = self.flock(100, cohesion)
        align_vel = self.align(100, alignment)
        avoid_vel = self.avoid(40, separation)
        target = self._target_vector()

        final_vel = (self.velocity + Vector2D(
            x=flock_vel.x + avoid_vel.x + align_vel.x + target.x,
            y=flock_vel.y + avoid_vel.y + align_vel.y + target.y,
        )).normalise()

        self.move(final_vel)
        self.avoid_walls()

    def avoid_walls(self):
        pad = 50
        turn = 2
        direction = Vector2D(0, 0)
        if (self.location.x < pad):
            direction.x += turn
        if (self.location.x > self.world.screen.get_width() - pad):
            direction.x -= turn
        if (self.location.y < pad):
            direction.y += turn
        if (self.location.y > self.world.screen.get_height() - pad):
            direction.y -= turn

        self.move(self.velocity + direction)
