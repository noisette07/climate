"""Petites fonctions de géométrie, faites maison (pas de shapely).

On travaille en coordonnées Lambert 93 (des mètres), donc les distances sont
directes. Une "forme" est une liste d'anneaux : le premier est le contour, les
suivants sont des trous ou des morceaux séparés.
"""

Point = list[float]        # [x, y] en mètres
Anneau = list[Point]
Forme = list[Anneau]
Boite = tuple[float, float, float, float]  # (x_min, y_min, x_max, y_max)


def boite_englobante(forme: Forme) -> Boite:
    """Renvoie le plus petit rectangle qui contient la forme."""
    xs = [p[0] for anneau in forme for p in anneau]
    ys = [p[1] for anneau in forme for p in anneau]
    return min(xs), min(ys), max(xs), max(ys)


def dans_boite(p: Point, boite: Boite) -> bool:
    """Le point est-il dans le rectangle ? (test rapide avant le vrai calcul)."""
    x_min, y_min, x_max, y_max = boite
    return x_min <= p[0] <= x_max and y_min <= p[1] <= y_max


def _traverse_anneau(p: Point, anneau: Anneau) -> int:
    """Compte combien de fois un rayon horizontal (vers la droite) coupe l'anneau."""
    x, y = p[0], p[1]
    traversees = 0
    n = len(anneau)
    for i in range(n):
        xi, yi = anneau[i]
        xj, yj = anneau[i - 1]
        if (yi > y) != (yj > y):
            x_intersection = xi + (y - yi) / (yj - yi) * (xj - xi)
            if x < x_intersection:
                traversees += 1
    return traversees


def point_dans_forme(p: Point, forme: Forme) -> bool:
    """Le point est-il dans la forme ?

    Astuce classique : on envoie un rayon horizontal depuis le point et on compte
    les côtés qu'il traverse. Nombre impair = dedans. En comptant sur tous les
    anneaux, un point tombé dans un trou est traversé 2 fois → il ressort dehors,
    ce qui est bien ce qu'on veut.
    """
    total = sum(_traverse_anneau(p, anneau) for anneau in forme)
    return total % 2 == 1


def simplifier(forme: Forme, seuil: float) -> Forme:
    """Enlève les points trop rapprochés pour alléger la forme.

    On garde un point seulement s'il est à plus de ``seuil`` mètres du dernier
    gardé. Un contour de commune peut avoir des dizaines de milliers de points :
    à l'échelle d'une grille de quelques centaines de mètres ça ne se voit pas,
    mais le test point-dans-forme devient beaucoup plus rapide.
    """
    seuil2 = seuil * seuil
    forme_simple: Forme = []
    for anneau in forme:
        garde = [anneau[0]]
        for p in anneau[1:]:
            dx, dy = p[0] - garde[-1][0], p[1] - garde[-1][1]
            if dx * dx + dy * dy >= seuil2:
                garde.append(p)
        forme_simple.append(garde)
    return forme_simple
