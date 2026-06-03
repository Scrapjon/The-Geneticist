import pygame
from data_types import *
from entities import *
from events import EventManager, InputKeys

class World:

    screen: pygame.Surface
    player: PlayerShip
    enemies: list[EnemyShip]
    event_manager: EventManager = EventManager()

    def __init__(self, screen: pygame.Surface, player: PlayerShip) -> None:
        self.screen = screen
        self.spawn_player(player)
        self.__add_player_inputs__()


    def spawn_player(self, player: PlayerShip):
        self.player = player

    def __add_player_inputs__(self):
        
        self.event_manager.add_input_event(
            InputKeys.W, 
            lambda: self.player.move(Vector2D(0,1))
        )
        self.event_manager.add_input_event(
            InputKeys.S,
            lambda: self.player.move(Vector2D(0,-1))
        )
        self.event_manager.add_input_event(
            InputKeys.D,
            lambda: self.player.move(Vector2D(1, 0))
        )
        self.event_manager.add_input_event(
            InputKeys.A,
            lambda: self.player.move(Vector2D(-1,0))
        )


    def spawn_enemy(self, enemy: EnemyShip):
        pass

    def update(self):

        self.event_manager.check_events()


        # fill the screen with a color to wipe away anything from last frame
        self.player.update()
        self.screen.fill("black")
        self.player.draw(self.screen)

        # flip() the display to put your work on screen
        pygame.display.flip()

    def should_exit(self):
        return self.event_manager.should_exit


