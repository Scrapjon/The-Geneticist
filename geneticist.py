from data_types import *
from entities import EnemyShip
from typing import List
from random import choices

Population = List[Genome]

@dataclass
class EnemyData:
    damage_dealt: float
    time_alive: float
    genome: Genome


class Geneticist:
    wave_num: int = 0
    enemies: list[EnemyShip]


    def __init__(self) -> None:
        self.enemies = []

    @property
    def enemy_count(self):
        return len(self.enemies)
    
    @staticmethod
    def generate_genome(length: int) -> Genome:
        return Genome(*choices(
            [i for i in range(100)],
            k=len(EMPTY_GENOME)
        ))
    
    def generate_population(self, size: int, genome_length: int) -> Population:
        return [self.generate_genome(genome_length) for _ in range(size)]
    

    def fitness(self, genome: Genome, enemies: List[EnemyShip], weight_limit: int) -> int:
        if len(genome) != len(enemies):
            raise ValueError("Genome and enemies must be of the same length")

        value = 0

        for i, enemy in enumerate(enemies):
            pass

        return value