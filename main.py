from world import World
from data_types.vector import Vector2D
from data_types.rotator import Rotator
from data_types.genome import Genome
from entities import *
import events
import pygame
import time
import random


def main():
    pygame.init()
    screen = pygame.display.set_mode((1280, 720))
    clock = pygame.time.Clock()
    running = True

    world = World(
        screen = screen,
        player = PlayerShip(
            location = Vector2D(100,100),
            rotation = 0,
            max_health = 100,
            speed = 2
        )
    )
    world.player.move(Vector2D(1,0)) # silly
    
    for i in range(10):
        world.spawn_enemy(
            EnemyShip(
                location = Vector2D(
                    random.randrange(0, 1280),
                    random.randrange(0, 720)
                ),
                rotation = random.randrange(0,360),
                max_health = 100, 
                world = world,
                genome=Genome(0.003,0.1,0.01,100,100,100,100)
            )
        )

    while running:       
        world.update()

        running = not world.should_exit()
        clock.tick(60)  # limits FPS to 60

    pygame.quit()

if __name__ == "__main__":
    main()