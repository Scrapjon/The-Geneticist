from dataclasses import dataclass
from random import randrange, sample
from typing import List, Optional

import config
from data_types import Genome, Vector2D
from data_types.genome import random_genome, crossover, mutate
from entities import EnemyShip

Population = List[Genome]


@dataclass
class EnemyData:
    """A finished agent's scoring record. One per enemy, per wave."""
    damage_dealt: float
    time_alive: float
    genome: Genome


class Geneticist:
    """
    The macro planner. Owns the live enemy list and the genome population, runs
    the evaluate -> select -> breed -> spawn cycle between waves, and keeps the
    handful of summary numbers the telemetry overlay reads.
    """

    def __init__(self) -> None:
        self.wave_num: int = 0
        self.enemies: list[EnemyShip] = []
        self.population: Population = []

        self.wave_active: bool = False
        self.wave_elapsed: float = 0.0
        self.total_damage_to_player: float = 0.0
        self.wave_records: list[EnemyData] = []

        # telemetry snapshots from the wave that just ended
        self.last_avg_lifespan: float = 0.0
        self.last_fittest_genome: Optional[Genome] = None
        self.last_fittest_score: float = 0.0

        # one record per generation for the evolution chart
        self.history: list[dict] = []
        self._chart_saved_on_death: bool = False

    @property
    def enemy_count(self):
        return len(self.enemies)

    @property
    def difficulty(self) -> float:
        # Starts at DIFFICULTY_BASE on wave 1, climbing linearly. Drives the
        # point-buy stat budget.
        return config.DIFFICULTY_BASE + (self.wave_num - 1) * config.DIFFICULTY_STEP

    # ----- population creation -----

    @staticmethod
    def generate_genome() -> Genome:
        return random_genome()

    def generate_population(self, size: int) -> Population:
        return [self.generate_genome() for _ in range(size)]

    # ----- live-wave bookkeeping -----

    def register_player_damage(self, amount: float):
        self.total_damage_to_player += amount

    def record_death(self, enemy: EnemyShip):
        """Called when the world culls a dead enemy. Stamps the death and files
        its scoring record."""
        if enemy.death_time is None:
            enemy.death_time = self.wave_elapsed
        self.wave_records.append(
            EnemyData(enemy.damage_dealt, enemy.death_time - enemy.spawn_time, enemy.genome)
        )

    # ----- wave lifecycle -----

    def start(self, world):
        self.wave_num = 1
        self.population = self.generate_population(config.POPULATION_SIZE)
        self.spawn_wave(world)

    def spawn_wave(self, world):
        self.wave_elapsed = 0.0
        self.total_damage_to_player = 0.0
        self.wave_records = []
        self.wave_active = True
        self._record_generation()

        for genome in self.population:
            enemy = EnemyShip(
                location=Vector2D(randrange(0, config.SCREEN_WIDTH), randrange(0, config.SCREEN_HEIGHT)),
                rotation=randrange(0, 360),
                world=world,
                genome=genome,
                difficulty=self.difficulty,
            )
            enemy.spawn_time = 0.0
            world.spawn_enemy(enemy)

    def tick(self, world):
        """Advance the wave clock and decide whether the wave is over. Called
        once per frame by the world after it has culled dead entities."""
        if not self.wave_active:
            return

        self.wave_elapsed += 1.0 / config.FPS

        if not world.player.alive:
            self.wave_active = False
            world.game_over = True
            if not self._chart_saved_on_death:
                self._chart_saved_on_death = True
                self.save_chart()
            return

        if self.enemy_count == 0:
            self.end_wave(world)
        elif self.wave_elapsed >= config.WAVE_TIME_LIMIT:
            # Anything still standing is a survivor. Recording them with their
            # (small) damage and long lifespan lets fitness sort out whether
            # turtling was actually worth anything.
            self.end_wave(world)

    def end_wave(self, world):
        # File records for any survivors before we wipe the board.
        for enemy in list(self.enemies):
            self.wave_records.append(
                EnemyData(enemy.damage_dealt, self.wave_elapsed - enemy.spawn_time, enemy.genome)
            )
        world.clear_enemies_and_projectiles()

        self.population = self.select_and_breed()

        # Heal the player back to full so each wave is judged on its own terms,
        # exactly as promised in the plan.
        world.player.health = world.player.max_health

        self.wave_num += 1
        self.spawn_wave(world)

        # Refresh the evolution chart between waves so whatever is on disk is
        # always current, even if the run ends with the window close. Quiet so
        # it doesn't spam the console every wave.
        self.save_chart(announce=False)

    def _record_generation(self):
        """Snapshot the mean of every gene across the population about to play.
        Recorded at spawn so a generation is logged even if the player dies in
        it and end_wave never runs."""
        if not self.population:
            return
        n = len(self.population)
        mean = [sum(g[i] for g in self.population) / n for i in range(len(self.population[0]))]
        self.history.append({"wave": self.wave_num, "mean": mean})

    def save_chart(self, announce: bool = True):
        """Render the genome-evolution chart to charts/. Wrapped so a charting
        hiccup can never take the game down with it."""
        if not self.history:
            return None
        try:
            from charts import save_genome_evolution
            path = save_genome_evolution(self.history)
            if path and announce:
                print(f"genome evolution chart saved to {path}")
            return path
        except Exception as exc:
            print(f"chart save failed: {exc}")
            return None

    # ----- the genetic algorithm -----

    def fitness(self, record: EnemyData) -> float:
        """
        fitness = (damage_dealt / total_damage_to_player) * time_alive

        The damage fraction sits in [0, 1] and acts as a weight on survival
        time. That ordering is deliberate: it kills the two degenerate
        strategies at once. Turtle in a corner and your damage fraction is ~0,
        so a long life scores nothing; rush in and trade your whole life for one
        hit and your time_alive is tiny. The agents that score are the ones that
        are a sustained threat. (The portfolio wrote this as a division by
        mistake, which would have rewarded dying fast. The plan's multiply is
        the version that matches the stated intent, so that is what ships.)
        """
        if self.total_damage_to_player <= 0:
            return 0.0
        return (record.damage_dealt / self.total_damage_to_player) * record.time_alive

    def select_and_breed(self) -> Population:
        if not self.wave_records:
            return self.generate_population(config.POPULATION_SIZE)

        scored = sorted(self.wave_records, key=self.fitness, reverse=True)

        # telemetry snapshot
        self.last_avg_lifespan = sum(r.time_alive for r in self.wave_records) / len(self.wave_records)
        self.last_fittest_genome = scored[0].genome
        self.last_fittest_score = self.fitness(scored[0])

        parents = [r.genome for r in scored[:config.TOP_N]]

        # If the whole wave scored zero (nobody touched the player) there is no
        # gradient to climb, so reseed with fresh randoms rather than inbreeding
        # a population of duds.
        if self.last_fittest_score <= 0:
            return self.generate_population(config.POPULATION_SIZE)

        next_pop: Population = []

        # Elitism: the very best carry through untouched so a good genome is
        # never lost to an unlucky mutation.
        for genome in parents[:config.ELITES]:
            next_pop.append(genome)

        while len(next_pop) < config.POPULATION_SIZE:
            if len(parents) >= 2:
                mum, dad = sample(parents, 2)
            else:
                mum = dad = parents[0]
            child = mutate(crossover(mum, dad))
            next_pop.append(child)

        return next_pop
