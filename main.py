import geneticist
from world import World
from data_types.vector import Vector2D
from data_types.rotator import Rotator
from entities import *
import events
import pygame
import time


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
            speed = 1
        )
    )
    world.player.move(Vector2D(1,0)) # silly

    while running:       
        world.update()

        running = not world.should_exit()
        print(world.player.rotation)
        clock.tick(60)  # limits FPS to 60

    pygame.quit()

if __name__ == "__main__":
    main()