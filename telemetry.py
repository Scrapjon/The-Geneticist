import pygame
import config
from entities.enemy import EnemyState, STATE_COLOURS


class Telemetry:
    """
    Heads-up overlay. The always-on line covers wave and enemy count; TAB
    reveals the debug block (lifespan, mutation sigma, last wave's fittest
    genome) exactly as scoped in the plan's telemetry table.
    """

    def __init__(self):
        self.debug = False
        if not pygame.font.get_init():
            pygame.font.init()
        self.font = pygame.font.SysFont("consolas", 18)
        self.small = pygame.font.SysFont("consolas", 15)
        self.big = pygame.font.SysFont("consolas", 48, bold=True)

    def toggle_debug(self):
        self.debug = not self.debug

    def _line(self, screen, text, x, y, colour=(230, 230, 230), font=None):
        font = font or self.font
        screen.blit(font.render(text, True, colour), (x, y))

    def draw(self, screen: pygame.Surface, world):
        g = world.geneticist
        x, y = 12, 10
        step = 22

        self._line(screen, f"WAVE {g.wave_num}", x, y); y += step
        self._line(screen, f"ENEMIES  {g.enemy_count} / {config.POPULATION_SIZE}", x, y); y += step
        self._line(screen, f"DIFFICULTY  x{g.difficulty:.2f}", x, y); y += step

        # player health bar
        ratio = max(0.0, world.player.health_ratio)
        self._line(screen, f"HP  {int(world.player.health)}/{int(world.player.max_health)}", x, y)
        bar_x = x + 130
        pygame.draw.rect(screen, (60, 60, 60), (bar_x, y + 3, 160, 14))
        pygame.draw.rect(screen, (0, 220, 90), (bar_x, y + 3, int(160 * ratio), 14))
        y += step + 6

        dash_ready = getattr(world.player, "dash_ready", True)
        dash_label = "DASH ready" if dash_ready else "DASH ..."
        dash_colour = (0, 220, 90) if dash_ready else (120, 120, 120)
        self._line(screen, dash_label, x, y, dash_colour, self.small); y += step
        self._line(screen, "TAB: debug", x, y, (120, 120, 120), self.small)

        if self.debug:
            self._draw_debug(screen, world, g)

        if getattr(world, "game_over", False):
            self._draw_game_over(screen)

    def _draw_debug(self, screen, world, g):
        x = config.SCREEN_WIDTH - 330
        y = 10
        step = 20

        self._line(screen, "── DEBUG ──", x, y, (180, 180, 255), self.small); y += step
        self._line(screen, f"wave time     {g.wave_elapsed:5.1f}s", x, y, font=self.small); y += step
        self._line(screen, f"dmg to player {g.total_damage_to_player:6.0f}", x, y, font=self.small); y += step
        self._line(screen, f"avg lifespan  {g.last_avg_lifespan:5.1f}s", x, y, font=self.small); y += step
        self._line(screen, f"mutation o    {config.POINT_BUY_SIGMA:.3f}", x, y, font=self.small); y += step

        y += 6
        self._line(screen, "fittest last wave:", x, y, (180, 180, 255), self.small); y += step
        gen = g.last_fittest_genome
        if gen is None:
            self._line(screen, "  (no data yet)", x, y, font=self.small); y += step
        else:
            pb = gen.point_buy
            self._line(screen, f"  score {g.last_fittest_score:.3f}", x, y, font=self.small); y += step
            self._line(screen, f"  sep/ali/coh {gen.separation:.3f} {gen.alignment:.3f} {gen.cohesion:.3f}", x, y, font=self.small); y += step
            self._line(screen, f"  hp   {pb.max_health:.2f}", x, y, font=self.small); y += step
            self._line(screen, f"  spd  {pb.max_speed:.2f}", x, y, font=self.small); y += step
            self._line(screen, f"  flee {pb.flee_threshold:.2f}", x, y, font=self.small); y += step
            self._line(screen, f"  dmg  {pb.damage:.2f}", x, y, font=self.small); y += step

        # state colour legend
        y += 8
        self._line(screen, "states:", x, y, (180, 180, 255), self.small); y += step
        for state in (EnemyState.PATROL, EnemyState.CHASE, EnemyState.ATTACK, EnemyState.FLEE):
            pygame.draw.rect(screen, STATE_COLOURS[state], (x, y + 2, 12, 12))
            self._line(screen, state.name, x + 20, y - 1, font=self.small)
            y += step

    def _draw_game_over(self, screen):
        text = self.big.render("GAME OVER", True, (255, 60, 60))
        rect = text.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2))
        screen.blit(text, rect)
        sub = self.font.render(
            "the geneticist wins", True, (200, 200, 200)
        )
        srect = sub.get_rect(center=(config.SCREEN_WIDTH // 2, config.SCREEN_HEIGHT // 2 + 44))
        screen.blit(sub, srect)
