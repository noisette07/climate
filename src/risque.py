"""Aléa inondation : une intensité par maille, à partir des zones du TRI.

Il y a trois scénarios (crue fréquente, moyenne, extrême). Une maille prend
l'intensité du scénario le plus fréquent qui la recouvre.

Marseille a ~5000 polygones inondables : tester chaque maille contre tous, ça
rame. Du coup je range les polygones dans une grille de cases de 1 km (un
"index spatial") et pour un point je ne regarde que les polygones de sa case.

(L'incendie, qui n'existe qu'à l'échelle de la commune, est traité à part dans
carte_incendies.py.)
"""

from geometrie import (
    Boite, Forme, Point, boite_englobante, dans_boite, point_dans_forme, simplifier,
)
from grille import Maille

# Une zone inondable prête à l'emploi : sa forme + sa boîte englobante.
FormeIndexee = tuple[Boite, Forme]
# L'index : case (i, j) -> zones dont la boîte touche cette case.
IndexSpatial = dict[tuple[int, int], list[FormeIndexee]]

# Taille d'une case de l'index, en mètres.
TAILLE_CASE = 1000.0


def _boites_se_croisent(a: Boite, b: Boite) -> bool:
    """Les deux rectangles se touchent-ils ?"""
    return not (a[2] < b[0] or a[0] > b[2] or a[3] < b[1] or a[1] > b[3])


def _case(x: float, y: float) -> tuple[int, int]:
    """La case de l'index qui contient le point (x, y)."""
    return int(x // TAILLE_CASE), int(y // TAILLE_CASE)


def construire_index(zones: list[Forme], clip: Boite | None = None) -> IndexSpatial:
    """Range les zones inondables dans l'index spatial.

    ``clip`` (la boîte de la commune) permet de jeter tout de suite les zones qui
    n'ont rien à voir : le TRI couvre tout un territoire, on ne garde que ce qui
    touche la commune. Chaque zone est mise dans toutes les cases que sa boîte
    recouvre.
    """
    index: IndexSpatial = {}
    for forme in zones:
        boite = boite_englobante(forme)
        if clip is not None and not _boites_se_croisent(boite, clip):
            continue
        # J'allège la zone au passage : certaines (le long de la côte) ont des
        # milliers de points. Invisible à notre échelle, mais bien plus rapide.
        forme = simplifier(forme, seuil=30.0)
        (i0, j0), (i1, j1) = _case(boite[0], boite[1]), _case(boite[2], boite[3])
        for i in range(i0, i1 + 1):
            for j in range(j0, j1 + 1):
                index.setdefault((i, j), []).append((boite, forme))
    return index


def _point_dans_index(p: Point, index: IndexSpatial) -> bool:
    """Le point est-il dans une zone ? On ne regarde que les zones de sa case."""
    for boite, forme in index.get(_case(p[0], p[1]), []):
        if dans_boite(p, boite) and point_dans_forme(p, forme):
            return True
    return False


def dans_scenario(maille: Maille, index: IndexSpatial) -> bool:
    """La maille est-elle inondée dans ce scénario ? (test sur son centre)."""
    return _point_dans_index(maille["centre"], index)
