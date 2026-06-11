# The Geneticist

A genetic-algorithm difficulty-scaling system bolted into a top-down arena
shooter. Instead of a fixed difficulty curve, the enemies evolve between waves to
specialise against however you happen to be playing. The name is a nod to The
Director in Left 4 Dead 2, except the Geneticist's only goal is to beat you.

COS30002 - AI for Games | Oliver Moloney - 104273068

## Running it

Recommended (uv reads the committed lockfile):

```
uv run main.py
```

Or with a plain venv:

```
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install pygame
python main.py
```

Needs Python 3.13+ and Pygame 2.6.1+.

## Controls

| Input        | Action                              |
|--------------|-------------------------------------|
| W / A / S / D | Move                               |
| Space        | Fire (in the direction you're facing)|
| Left Shift   | Dash (quick dodge, short cooldown)  |
| TAB          | Toggle the debug telemetry panel    |
| Window close | Quit                                |

## How a wave works

Each enemy carries a genome. Three genes are boid steering weights (separation,
alignment, cohesion) and four are point-buy stats (max health, max speed, flee
threshold, damage) that always sum to 1.0, so an enemy can never be good at
everything at once.

1. A wave of enemies spawns from the current population.
2. They flock, chase, attack and flee through a genome-driven FSM.
3. When the wave clears (or hits the time cap) every enemy is scored by

   ```
   fitness = (damage_dealt / total_damage_to_player) * time_alive
   ```

4. The top performers are selected, crossed over, and Gaussian-mutated into the
   next generation.
5. You get healed to full, difficulty ticks up, and the next wave spawns built
   from the survivors of the last one.

Enemies change colour by FSM state: grey patrol, orange chase, red attack, blue
flee. The TAB panel shows wave time, damage dealt to you, average lifespan,
mutation sigma, and the full genome of last wave's fittest enemy.

## Layout

```
main.py            entry point, owns the loop
world.py           mediator: entities, collision, wave ticking, render
geneticist.py      population, fitness, selection/crossover/mutation, wave loop
telemetry.py       HUD overlay
events.py          key -> callback input system
config.py          every tunable in one place
data_types/        vectors, triangle, circle, genome + GA operators
entities/          Entity -> Ship -> Player/Enemy, plus Projectile
```
