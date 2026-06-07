import pygame
from data_types import *
from entities import *
from events import EventManager, InputKeys

class World:

    screen: pygame.Surface
    player: PlayerShip
    entities: list[Entity] = []
    enemies: list[EnemyShip] = []
    event_manager: EventManager = EventManager()

    def __init__(self, screen: pygame.Surface, player: PlayerShip, ) -> None:
        self.screen = screen
        self.spawn_player(player)
        self.__add_player_inputs__()


    def spawn_player(self, player: PlayerShip):
        self.player = player
        self.entities.append(player)

    def __add_player_inputs__(self):
        
        self.event_manager.add_input_event(
            InputKeys.W, 
            lambda: self.player.move(Vector2D(0,-1))
        )
        self.event_manager.add_input_event(
            InputKeys.S,
            lambda: self.player.move(Vector2D(0,1))
        )
        self.event_manager.add_input_event(
            InputKeys.D,
            lambda: self.player.move(Vector2D(1, 0))
        )
        self.event_manager.add_input_event(
            InputKeys.A,
            lambda: self.player.move(Vector2D(-1,0))
        )
        self.event_manager.add_input_event(
            InputKeys.SPACE,
            lambda: self.player.shoot(self)
        )

    def handle_collision(self):
        pass

    def spawn_enemy(self, enemy: EnemyShip):
        self.enemies.append(enemy)
        self.entities.append(enemy)

    def spawn_projectile(self, projectile: Projectile):
        self.entities.append(projectile)

    def update(self):

        self.event_manager.check_events()


        # fill the screen with a color to wipe away anything from last frame
        self.screen.fill("black")
        to_remove = []
        for entity in self.entities:
            if entity.alive == False:
                to_remove.append(entity)
                continue
            entity.update(world=self)
            entity.draw(self.screen)
            entity.handle_collision(self)
        
        for entity in to_remove:
            self.entities.remove(entity)
            del entity

        # flip() the display to put your work on screen
        pygame.display.flip()

    def should_exit(self):
        return self.event_manager.should_exit


