"""Tile-based stage definitions for early floors.

Legend:
    B = Block (solid wall/platform)
    P = Player spawn point
    E = Enemy spawn point (generic)
    M = Melee enemy spawn
    R = Ranged enemy spawn
    H = Hazard
    . = Empty space
"""

TILE_SIZE = 32  # Pixels per tile

STAGE_1 = [
    'BBBBBBBBBBBBBBBBBBBBBBBBB',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B...P............E.E....B',
    'BBBBBBBBBBBBBBBBBBBBBBBBB',
]

STAGE_2 = [
    'BBBBBBBBBBBBBBBBBBBBBBBBB',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B............E..........B',
    'B........BBBBBBB........B',
    'B..P................E...B',
    'BBBBBBB...........BBBBBBB',
    'BBBBBBBBBBBBBBBBBBBBBBBBB',
]

STAGE_3 = [
    'BBBBBBBBBBBBBBBBBBBBBBBBB',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B.......................B',
    'B..P.............E..E...B',
    'BBBBBBBBB.......BBBBBBBBB',
    'B.......................B',
    'B......BBBBBBBBBBB......B',
    'B.......................B',
    'B.......................B',
    'BHHHHHHHHHHHHHHHHHHHHHHHB',
    'B.......................B',
    'B.......................B',
    'BBBBBBBBBBBBBBBBBBBBBBBBB',
]

# Map floor numbers to stages (floors 1-3 use tile maps, 4+ use procedural)
TILE_STAGES = {
    1: STAGE_1,
    2: STAGE_2,
    3: STAGE_3,
}


def get_stage(floor_number):
    """Get the tile map for a floor, or None if procedural should be used."""
    return TILE_STAGES.get(floor_number, None)
