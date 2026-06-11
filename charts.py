"""
Draws a genome-evolution line chart and dumps it to a PNG in charts/. Rendered
with pygame on purpose so the project keeps its one-dependency promise instead of
dragging in matplotlib just for one graph.

Each gene gets its own colour. The boid weights and the point-buy stats live on
wildly different scales (steering weights are ~0.001, the point-buy fractions sum
to 1.0), so cramming all seven onto one axis would flatten the boid lines into
the floor. They get a panel each, sharing the wave axis.
"""

import os
import pygame

# index-aligned to the Genome fields: sep, ali, coh, max_health, max_speed,
# flee_threshold, damage
GENE_NAMES = ["separation", "alignment", "cohesion",
              "max_health", "max_speed", "flee_threshold", "damage"]
GENE_COLOURS = [
    (220, 50, 47),    # separation     - red
    (60, 160, 60),    # alignment      - green
    (40, 110, 220),   # cohesion       - blue
    (240, 150, 20),   # max_health     - orange
    (150, 60, 200),   # max_speed      - purple
    (0, 170, 170),    # flee_threshold - teal
    (210, 60, 160),   # damage         - magenta
]
BOID_IDX = [0, 1, 2]
POINT_BUY_IDX = [3, 4, 5, 6]

WIDTH, HEIGHT = 1100, 760
BG = (250, 250, 250)
AXIS = (40, 40, 40)
GRID = (224, 224, 224)
TEXT = (30, 30, 30)


def _font(size, bold=False):
    if not pygame.font.get_init():
        pygame.font.init()
    return pygame.font.SysFont("consolas", size, bold=bold)


def _draw_panel(surface, rect, title, waves, series, panel_font, small):
    x, y, w, h = rect
    pygame.draw.rect(surface, AXIS, rect, 1)
    surface.blit(panel_font.render(title, True, TEXT), (x + 6, y - 26))

    all_vals = [v for _, _, vals in series for v in vals]
    if not all_vals:
        return

    vmin = 0.0
    vmax = max(all_vals) * 1.1
    if vmax <= 0:
        vmax = 1.0

    wmin = waves[0]
    wmax = waves[-1] if waves[-1] != waves[0] else waves[0] + 1

    def px(wave):
        if wmax == wmin:
            return x
        return x + (wave - wmin) / (wmax - wmin) * w

    def py(val):
        return y + h - (val - vmin) / (vmax - vmin) * h

    # y gridlines + labels
    for i in range(6):
        gv = vmin + (vmax - vmin) * i / 5
        gy = py(gv)
        pygame.draw.line(surface, GRID, (x, gy), (x + w, gy), 1)
        surface.blit(small.render(f"{gv:.3f}", True, TEXT), (x - 58, gy - 8))

    # x gridlines + wave labels (thin them out if there are lots)
    step = max(1, len(waves) // 12)
    for i in range(0, len(waves), step):
        gx = px(waves[i])
        pygame.draw.line(surface, GRID, (gx, y), (gx, y + h), 1)
        surface.blit(small.render(str(waves[i]), True, TEXT), (gx - 6, y + h + 4))

    # the actual series
    for _, colour, vals in series:
        pts = [(px(waves[i]), py(vals[i])) for i in range(len(vals))]
        if len(pts) >= 2:
            pygame.draw.lines(surface, colour, False, pts, 2)
        for p in pts:
            pygame.draw.circle(surface, colour, (int(p[0]), int(p[1])), 3)


def save_genome_evolution(history, folder="charts", filename="genome_evolution.png"):
    """
    history: list of {"wave": int, "mean": [7 floats]} records, one per wave.
    Writes a PNG and returns its path, or None if there was nothing to draw.
    """
    if not history:
        return None

    os.makedirs(folder, exist_ok=True)
    if not pygame.get_init():
        pygame.init()

    waves = [rec["wave"] for rec in history]
    means = [rec["mean"] for rec in history]

    surface = pygame.Surface((WIDTH, HEIGHT))
    surface.fill(BG)

    title_font = _font(24, bold=True)
    panel_font = _font(18, bold=True)
    small = _font(13)

    surface.blit(
        title_font.render("Genome evolution (population mean per wave)", True, TEXT),
        (60, 18),
    )

    pad_left, pad_right, pad_top = 70, 230, 72
    panel_w = WIDTH - pad_left - pad_right
    panel_h = 248
    gap = 76

    boid_series = [(GENE_NAMES[i], GENE_COLOURS[i], [m[i] for m in means]) for i in BOID_IDX]
    pb_series = [(GENE_NAMES[i], GENE_COLOURS[i], [m[i] for m in means]) for i in POINT_BUY_IDX]

    _draw_panel(surface, (pad_left, pad_top, panel_w, panel_h),
                "boid steering weights", waves, boid_series, panel_font, small)
    _draw_panel(surface, (pad_left, pad_top + panel_h + gap, panel_w, panel_h),
                "point-buy stats (normalised, sum to 1.0)", waves, pb_series, panel_font, small)

    # legend down the right side
    lx = WIDTH - pad_right + 36
    ly = pad_top
    surface.blit(panel_font.render("genes", True, TEXT), (lx, ly - 26))
    for i, name in enumerate(GENE_NAMES):
        yy = ly + i * 28
        pygame.draw.rect(surface, GENE_COLOURS[i], (lx, yy + 3, 16, 12))
        surface.blit(small.render(name, True, TEXT), (lx + 26, yy))

    surface.blit(small.render("wave", True, TEXT), (pad_left + panel_w // 2 - 12, HEIGHT - 22))

    path = os.path.join(folder, filename)
    pygame.image.save(surface, path)
    return path
