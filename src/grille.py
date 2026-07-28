"""Découpe la commune en petits carrés (la "grille").

Comme on est en Lambert 93 (des mètres), le pas est directement en mètres.
"""

from geometrie import Forme, Point, boite_englobante, point_dans_forme

# Une maille : son centre et ses coins (x0, y0, x1, y1), en mètres.
Maille = dict[str, object]


def construire_grille(commune: Forme, pas: float) -> list[Maille]:
    """Fabrique la grille de carrés de côté ``pas`` et ne garde que ceux qui
    tombent dans la commune (test sur le centre du carré)."""
    x_min, y_min, x_max, y_max = boite_englobante(commune)
    mailles: list[Maille] = []

    y0 = y_min
    while y0 < y_max:
        x0 = x_min
        while x0 < x_max:
            centre: Point = [x0 + pas / 2, y0 + pas / 2]
            if point_dans_forme(centre, commune):
                mailles.append({
                    "centre": centre,
                    "coins": [x0, y0, x0 + pas, y0 + pas],
                })
            x0 += pas
        y0 += pas

    return mailles
