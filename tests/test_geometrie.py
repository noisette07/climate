"""Petits tests pour geometrie.py.

L'idée d'un test : je donne une entrée dont je connais le résultat, et je vérifie
avec assert que la fonction renvoie bien ça. Si plus tard je casse le code sans
faire exprès, le test plante et me prévient.

Ici je teste surtout point_dans_forme (le lancer de rayon).

Lancer depuis la racine du dépôt :
    python3 tests/test_geometrie.py
"""

import sys
from pathlib import Path

# Pour pouvoir importer les modules de src/ (les tests sont à côté).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from geometrie import boite_englobante, dans_boite, point_dans_forme

# Un carre simple de 10 x 10, defini comme une forme (liste d'un seul anneau).
CARRE = [[[0, 0], [10, 0], [10, 10], [0, 10]]]


def test_point_dedans():
    # Le centre du carre est clairement a l'interieur.
    assert point_dans_forme([5, 5], CARRE) is True


def test_point_dehors():
    # Un point loin du carre est a l'exterieur.
    assert point_dans_forme([20, 5], CARRE) is False


def test_point_dans_un_trou():
    # Forme avec un trou : anneau exterieur 10x10, trou central 4..6.
    # Un point dans le trou doit etre considere DEHORS (regle pair/impair).
    forme_trouee = [
        [[0, 0], [10, 0], [10, 10], [0, 10]],   # contour exterieur
        [[4, 4], [6, 4], [6, 6], [4, 6]],        # trou
    ]
    assert point_dans_forme([5, 5], forme_trouee) is False
    # Mais un point entre le trou et le bord reste DEDANS.
    assert point_dans_forme([1, 1], forme_trouee) is True


def test_boite_englobante():
    assert boite_englobante(CARRE) == (0, 0, 10, 10)


def test_dans_boite():
    boite = (0, 0, 10, 10)
    assert dans_boite([5, 5], boite) is True
    assert dans_boite([15, 5], boite) is False


if __name__ == "__main__":
    # Petit lanceur maison : execute toutes les fonctions test_*.
    tests = [f for nom, f in sorted(globals().items()) if nom.startswith("test_")]
    for test in tests:
        test()
        print("OK :", test.__name__)
    print(f"\n{len(tests)} tests passes.")
