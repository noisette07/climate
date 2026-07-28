"""Lecture des fichiers de données.

- Inondation : shapefiles du TRI 2020 (zones inondables), lus avec pyshp.
  Coordonnées en Lambert 93, attributs encodés en latin-1.
- Incendie : export CSV de la BDIFF. Séparateur ";", encodage UTF-8, et
  quelques lignes de blabla avant la vraie ligne d'en-tête.
"""

import csv
from pathlib import Path

import shapefile  # pyshp

from geometrie import Forme

# Un feu retenu : son année et la surface parcourue (en m²).
Incendie = dict[str, float]


def _shape_vers_forme(shape) -> Forme:
    """Transforme une géométrie pyshp en forme (liste d'anneaux)."""
    points = [list(pt) for pt in shape.points]
    debuts = list(shape.parts) + [len(points)]
    return [points[debuts[i]:debuts[i + 1]] for i in range(len(shape.parts))]


def lire_formes(chemin: Path) -> list[Forme]:
    """Lit toutes les géométries d'un shapefile."""
    lecteur = shapefile.Reader(str(chemin), encoding="latin-1")
    return [_shape_vers_forme(sh) for sh in lecteur.shapes()]


def lire_commune(chemin: Path, nom: str) -> Forme:
    """Cherche une commune par son nom (champ ``nom_com``) et renvoie son contour."""
    lecteur = shapefile.Reader(str(chemin), encoding="latin-1")
    champs = [c[0] for c in lecteur.fields[1:]]
    for enreg in lecteur.shapeRecords():
        attributs = dict(zip(champs, enreg.record))
        if attributs["nom_com"] == nom:
            return _shape_vers_forme(enreg.shape)
    raise ValueError(f"Commune introuvable dans le shapefile : {nom}")


def _lignes_incendies(chemin: Path):
    """Parcourt les lignes du CSV BDIFF (un dict par feu).

    On saute les lignes de métadonnées du début jusqu'à trouver l'en-tête (celui
    qui commence par "Année").
    """
    with open(chemin, encoding="utf-8") as fichier:
        colonnes = None
        for ligne in csv.reader(fichier, delimiter=";"):
            if colonnes is None:
                if ligne and ligne[0].strip().lower().startswith("ann"):
                    colonnes = ligne
                continue
            yield dict(zip(colonnes, ligne))


def incendies_par_commune(chemin: Path) -> dict[str, list[Incendie]]:
    """Range les feux du CSV par code INSEE de commune.

    Renvoie ``{code_insee: [ {annee, surface_m2}, ... ]}``.
    """
    par_commune: dict[str, list[Incendie]] = {}
    for enreg in _lignes_incendies(chemin):
        insee = enreg.get("Code INSEE")
        if not insee:
            continue
        par_commune.setdefault(insee, []).append({
            "annee": int(enreg["Année"]),
            "surface_m2": float(enreg["Surface parcourue (m2)"] or 0),
        })
    return par_commune
