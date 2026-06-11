"""
Global knobs for the whole sim. The Task 18 plan listed a config.py and I never
got around to it, so everything that used to be a magic number scattered across
files now lives here. If a value gets tweaked during balancing this is the only
place it should need to change.
"""

# --- display / loop ---
FPS = 60
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720

# --- population / GA ---
POPULATION_SIZE = 10        # enemies per wave
TOP_N = 4                   # parents carried into the next generation
ELITES = 2                  # best genomes copied straight through, unmutated
MUTATION_RATE = 0.6         # per-gene chance of being nudged
POINT_BUY_SIGMA = 0.08      # gaussian std for point-buy genes (they live in [0,1])
BOID_SIGMA = 0.006          # gaussian std for steering weights (much smaller scale)

# --- difficulty ---
# difficulty = DIFFICULTY_BASE + (wave - 1) * DIFFICULTY_STEP. Base sits under
# 1.0 so the opening wave is actually survivable; it climbs from there. Combat
# stats (health, damage) get multiplied by this.
DIFFICULTY_BASE = 0.65
DIFFICULTY_STEP = 0.12

# --- steering weight bounds (used for generation AND post-mutation clamping) ---
# Informed by the values that gave stable swarms during boid debugging. avoid()
# sums weighted closeness so its weight has to be tiny or the swarm explodes.
BOID_BOUNDS = {
    "separation": (0.0005, 0.02),
    "alignment":  (0.0,    0.20),
    "cohesion":   (0.0,    0.05),
}

# --- point-buy phenotype mapping ---
# Each point-buy gene is a fraction of a budget that all four genes share (they
# sum to 1.0). actual = base + budget * fraction * difficulty for the combat
# stats. flee_threshold is a threshold, not a "bigger is better" stat, so it
# maps straight onto an HP ratio and ignores difficulty (see the post-mortem).
HEALTH_BASE,  HEALTH_BUDGET  = 35,  90
SPEED_BASE,   SPEED_BUDGET   = 1.5, 3.5
DAMAGE_BASE,  DAMAGE_BUDGET  = 2,   12
FLEE_MIN,     FLEE_MAX       = 0.0, 0.6

# --- combat ---
PLAYER_DAMAGE        = 25      # flat damage per player projectile
PLAYER_FIRE_COOLDOWN = 0.18    # seconds, stops the player firing every frame
ENEMY_ATTACK_RANGE   = 280     # distance at which an enemy switches to ATTACK
ENEMY_DETECT_RANGE   = 520     # distance at which PATROL becomes CHASE
ENEMY_FIRE_COOLDOWN  = 1.6     # seconds between enemy shots (was punishingly low)

# --- steering powers per FSM state ---
CHASE_POWER = 1.4
FLEE_POWER  = 1.8

# --- player dash ---
DASH_SPEED_MULT = 5.0   # dash velocity = normal cruise speed * this
DASH_DURATION   = 0.16  # seconds the burst lasts
DASH_COOLDOWN   = 0.9   # seconds before you can dash again

# A wave that never clears (a maxed-flee enemy hugging a wall) would stall the
# whole loop, so hard-cap wave length. Survivors get scored as survivors, which
# is its own selection pressure against pure cowardice.
WAVE_TIME_LIMIT = 60.0
