from math import sin, cos, radians, sqrt
from pathlib import Path
from typing import Any

from pygame import Surface

from data_types import Rotator, Vector2D, BoidData, Genome

from .ship import Ship

class EnemyShip(Ship):

    genome: Genome

    def __init__(self, location: Vector2D, rotation: float, max_health: float, world, genome: Genome):
        super().__init__(location, rotation, max_health)
        self.color = (255, 0, 0)
        self.world = world
        self.genome = genome

    @property
    def boid_data(self):
        return BoidData(self.genome.separation, self.genome.alignment, self.genome.cohesion)

    def draw(self, screen: Surface):
        return super().draw(screen)
    
    def update(self, *args: Any, **kwargs: Any) -> None:
        #p_loc = self.world.player.location
        #goal_dir = p_loc - self.location
        #goal_dir = goal_dir.normalise()
        self.advance()
        return super().update(*args, **kwargs)
    
    def move(self, direction: Vector2D):
        min_speed = 1
        max_speed = 5
        speed = direction.length()
        normalised_dir = direction.normalise()
        if speed > max_speed:
            direction = normalised_dir * max_speed
        if speed < min_speed:
            direction = normalised_dir * min_speed
        
        return super().move(direction)
    
    def flock(self, boids, distance, power) -> Vector2D:
        neighbors: list[EnemyShip] = []
        for neighbor in boids:
            if (neighbor.location - self.location).length_sq() < distance * distance:
                neighbors.append(neighbor)
        mean_x = sum([neighbor.location.x for neighbor in neighbors]) / len(neighbors)
        mean_y = sum([neighbor.location.y for neighbor in neighbors]) / len(neighbors)
        delta_center_x = mean_x - self.location.x
        delta_center_y = mean_y - self.location.y
        return Vector2D(delta_center_x * power, delta_center_y * power)

    def align(self, boids, distance: float, power: float):
        neighbors: list[EnemyShip] = []
        for neighbor in boids:
            if (neighbor.location - self.location).length_sq() < distance * distance:
                neighbors.append(neighbor)
        mean_x_vel = sum([neighbor.velocity.x for neighbor in neighbors]) / len(neighbors)
        mean_y_vel = sum([neighbor.velocity.y for neighbor in neighbors]) / len(neighbors)
        dir_x_vel = mean_x_vel - self.velocity.x
        dir_y_vel = mean_y_vel - self.velocity.y
        
        return Vector2D(dir_x_vel * power, dir_y_vel * power)
    
    def avoid(self, boids, distance: float, power: float):
        neighbors: list[EnemyShip] = []
        for neighbor in boids:
            if (neighbor.location - self.location).length_sq() < distance * distance:
                neighbors.append(neighbor)
        sum_closeness_x, sum_closeness_y = 0, 0

        for neighbor in neighbors:
            closeness = distance - (self.location - neighbor.location).length()
            sum_closeness_x += (self.location.x - neighbor.location.x) * closeness
            sum_closeness_y += (self.location.y - neighbor.location.y) * closeness

        return Vector2D(sum_closeness_x * power, sum_closeness_y * power)
        

    def advance(self):
        separation, alignment, cohesion = self.boid_data
        flock_vel = self.flock(self.world.enemies, 100, cohesion)
        align_vel = self.align(self.world.enemies, 100, alignment)
        avoid_vel = self.avoid(self.world.enemies, 40, separation)
        
        final_vel = (self.velocity + Vector2D(
                x=flock_vel.x + avoid_vel.x + align_vel.x,
                y=flock_vel.y + avoid_vel.y + align_vel.y
            )).normalise()

        self.move(final_vel)
        self.avoid_walls()

    def avoid_walls(self):
        pad = 50
        turn = 2
        direction = Vector2D(0,0)
        if (self.location.x < pad):
            direction.x += turn
        if (self.location.x > self.world.screen.get_width() - pad):
            direction.x -= turn
        if (self.location.y < pad):
            direction.y += turn
        if (self.location.y > self.world.screen.get_height() - pad):
            direction.y -= turn
        
        self.move(self.velocity + direction)
    

