from world import World
from data_types.vector import Vector2D
from entities import *
import config
import pygame


def main():
    pygame.init()
    screen = pygame.display.set_mode((config.SCREEN_WIDTH, config.SCREEN_HEIGHT))
    clock = pygame.time.Clock()
    running = True

    world = World(
        screen=screen,
        player=PlayerShip(
            location=Vector2D(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2),
            rotation=0,
            max_health=120,
            speed=3,
        ),
    )

    # Hand off to the Geneticist for wave 1. Everything after this is the
    # evaluate -> select -> breed -> spawn loop running on its own.
    world.begin()

    while running:
        world.update()
        running = not world.should_exit()
        clock.tick(config.FPS)

    pygame.quit()


if __name__ == "__main__":
    main()
