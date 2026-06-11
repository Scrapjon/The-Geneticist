import pygame
from geneticist import Geneticist
from data_types import *
from entities import *
from events import EventManager, InputKeys
from telemetry import Telemetry


class World:

    def __init__(self, screen: pygame.Surface, player: PlayerShip) -> None:
        # Instance-owned state. These used to be class attributes, which quietly
        # shared one entity list across every World; harmless with a single
        # world but a trap waiting to happen, so they live on the instance now.
        self.screen = screen
        self.entities: list[Entity] = []
        self.event_manager = EventManager()
        self.geneticist = Geneticist()
        self.telemetry = Telemetry()
        self.game_over = False

        self.spawn_player(player)
        self.__add_player_inputs__()

    # enemies is still just a window onto the Geneticist's list so there is one
    # source of truth for the population.
    def __get_enemies__(self) -> list[EnemyShip]:
        return self.geneticist.enemies

    def __set_enemies__(self, enemies: list[EnemyShip]):
        self.geneticist.enemies = enemies

    enemies = property(fget=__get_enemies__, fset=__set_enemies__)

    def __add_player_inputs__(self):
        self.event_manager.add_input_event(InputKeys.W, lambda: self.player.move(Vector2D(0, -1)))
        self.event_manager.add_input_event(InputKeys.S, lambda: self.player.move(Vector2D(0, 1)))
        self.event_manager.add_input_event(InputKeys.D, lambda: self.player.move(Vector2D(1, 0)))
        self.event_manager.add_input_event(InputKeys.A, lambda: self.player.move(Vector2D(-1, 0)))
        self.event_manager.add_input_event(InputKeys.SPACE, lambda: self.player.shoot(self))
        self.event_manager.add_input_event(InputKeys.LSHIFT, lambda: self.player.dash())
        self.event_manager.add_input_event(InputKeys.TAB, lambda: self.telemetry.toggle_debug())

    def begin(self):
        """Kick off wave 1. Pulled out of __init__ so construction stays side
        effect free."""
        self.geneticist.start(self)

    def handle_collision(self):
        pass

    def spawn_player(self, player: PlayerShip):
        self.player = player
        self.entities.append(player)

    def spawn_enemy(self, enemy: EnemyShip):
        self.enemies.append(enemy)
        self.entities.append(enemy)

    def destroy_entity(self, entity: Entity):
        if entity in self.entities:
            self.entities.remove(entity)
        if issubclass(type(entity), EnemyShip):
            if entity in self.enemies:
                self.enemies.remove(entity)
            # File the dead enemy's fitness record on the way out.
            self.geneticist.record_death(entity)

    def spawn_projectile(self, projectile: Projectile):
        self.entities.append(projectile)

    def clear_enemies_and_projectiles(self):
        """Wipe the board between waves without routing survivors through
        record_death (the geneticist scores them itself)."""
        self.entities = [e for e in self.entities if e is self.player]
        self.geneticist.enemies = []

    def update(self):
        self.event_manager.check_events()
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
            self.destroy_entity(entity)

        # Advance the wave state machine after the board has settled for this
        # frame, then paint the overlay on top of everything.
        self.geneticist.tick(self)
        self.telemetry.draw(self.screen, self)

        pygame.display.flip()

    def should_exit(self):
        return self.event_manager.should_exit
