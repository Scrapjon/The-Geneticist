from dataclasses import dataclass
from random import gauss, random, randint, uniform
from typing import NamedTuple

import config
from .vector import Vector2D


@dataclass
class BoidData:
    separation: float
    alignment: float
    cohesion: float

    def __iter__(self):
        yield self.separation
        yield self.alignment
        yield self.cohesion


@dataclass
class PointBuy:
    # Point-buy mods
    max_health: float
    max_speed: float
    flee_threshold: float
    damage: float

    def __iter__(self):
        yield self.max_health
        yield self.max_speed
        yield self.flee_threshold
        yield self.damage


class Genome(NamedTuple):
    # Boids stuff
    separation: float
    alignment: float
    cohesion: float

    # Point-buy mods
    max_health: float
    max_speed: float
    flee_threshold: float
    damage: float

    @property
    def boid_data(self) -> BoidData:
        return BoidData(self.separation, self.alignment, self.cohesion)

    @property
    def point_buy(self) -> PointBuy:
        return PointBuy(self.max_health, self.max_speed, self.flee_threshold, self.damage)

    def __len__(self) -> int:
        # NamedTuple already knows its field count; calling list(self) here
        # recurses because list() asks the object for its length.
        return len(self._fields)


EMPTY_GENOME = Genome(0, 0, 0, 0, 0, 0, 0)

# The genome splits cleanly down the middle: the first three fields are steering
# weights, the last four are the point-buy stats. A lot of the operators below
# only want one half at a time so these indices keep that intent obvious.
BOID_SLICE = slice(0, 3)
POINT_BUY_SLICE = slice(3, 7)


def _clamp(value: float, low: float, high: float) -> float:
    return max(low, min(high, value))


def normalise_point_buy(genome: Genome) -> Genome:
    """
    Force the four point-buy genes to sum to exactly 1.0 while leaving the boid
    weights untouched. This is the constraint from the plan (akin to D&D point
    buy) that stops enemies from just evolving to be strong at everything. If
    the four genes happen to sum to zero we fall back to an even split rather
    than dividing by zero.
    """
    pb = list(genome)[POINT_BUY_SLICE]
    pb = [max(0.0, v) for v in pb]  # negatives make no sense for a budget share
    total = sum(pb)

    if total == 0:
        pb = [0.25, 0.25, 0.25, 0.25]
    else:
        pb = [v / total for v in pb]

    return Genome(*list(genome)[BOID_SLICE], *pb)


def random_genome() -> Genome:
    """
    Build one fresh genome for an initial population. Boid weights are drawn
    inside their stable bounds, point-buy genes are drawn at random and then
    normalised so the new genome already satisfies the sum-to-1.0 rule.
    """
    sep = uniform(*config.BOID_BOUNDS["separation"])
    ali = uniform(*config.BOID_BOUNDS["alignment"])
    coh = uniform(*config.BOID_BOUNDS["cohesion"])
    pb = [random() for _ in range(4)]
    return normalise_point_buy(Genome(sep, ali, coh, *pb))


def crossover(parent_a: Genome, parent_b: Genome) -> Genome:
    """
    Single-point crossover. NamedTuple -> list lets me splice at an index and
    rejoin, which was the whole reason the genome is a tuple in the first place.
    The cut never lands at the very ends so a child always inherits from both
    parents. The point-buy half is renormalised afterwards because splicing two
    already-normalised halves almost never sums back to 1.0.
    """
    a, b = list(parent_a), list(parent_b)
    cut = randint(1, len(a) - 1)
    child = Genome(*(a[:cut] + b[cut:]))
    return normalise_point_buy(child)


def mutate(genome: Genome) -> Genome:
    """
    Gaussian mutation. Every gene gets an independent roll against MUTATION_RATE;
    the ones that pass get a normal-distributed nudge. Steering weights and
    point-buy genes live on completely different scales so they use different
    sigmas and different clamps. Re-normalise the point-buy half at the end.
    """
    sep, ali, coh, mh, ms, ft, dmg = genome

    if random() < config.MUTATION_RATE:
        sep = _clamp(sep + gauss(0, config.BOID_SIGMA), *config.BOID_BOUNDS["separation"])
    if random() < config.MUTATION_RATE:
        ali = _clamp(ali + gauss(0, config.BOID_SIGMA), *config.BOID_BOUNDS["alignment"])
    if random() < config.MUTATION_RATE:
        coh = _clamp(coh + gauss(0, config.BOID_SIGMA), *config.BOID_BOUNDS["cohesion"])

    pb = [mh, ms, ft, dmg]
    for i in range(len(pb)):
        if random() < config.MUTATION_RATE:
            pb[i] = max(0.0, pb[i] + gauss(0, config.POINT_BUY_SIGMA))

    return normalise_point_buy(Genome(sep, ali, coh, *pb))
