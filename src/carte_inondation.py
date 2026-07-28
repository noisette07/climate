"""Carte interactive de l'inondation avec folium (fond OpenStreetMap).

folium veut des coordonnées en longitude/latitude, mais mes données sont en
Lambert 93 (des mètres). Je reprojette donc avec pyproj avant de dessiner.

Une couche par scénario de crue (fréquente / moyenne / extrême), qu'on peut
afficher ou cacher. Les zones sont emboîtées : l'extrême englobe la fréquente.
Le résultat est un fichier HTML à ouvrir dans le navigateur.
"""

import folium
from pyproj import Transformer

from geometrie import Forme
from grille import Maille

# Passage Lambert 93 (EPSG:2154) -> longitude/latitude (EPSG:4326).
_TRANSFO = Transformer.from_crs(2154, 4326, always_xy=True)

# Les scénarios, du plus large (rare) au plus petit (fréquent), avec leur nom
# affiché et leur couleur. On les dessine dans cet ordre pour que la zone
# fréquente (bleu foncé) reste bien visible par-dessus.
SCENARIOS = [
    ("faible", "Crue extrême (rare)", "#9ecae1"),
    ("moyen", "Crue moyenne", "#3182bd"),
    ("fort", "Crue fréquente", "#08519c"),
]


def _vers_lonlat(x: float, y: float) -> tuple[float, float]:
    """Convertit un point Lambert 93 en (longitude, latitude)."""
    lon, lat = _TRANSFO.transform(x, y)
    return lon, lat


def _coins_maille_latlon(maille: Maille) -> list[list[float]]:
    """Les 4 coins d'une maille en [lat, lon] (l'ordre voulu par folium)."""
    x0, y0, x1, y1 = maille["coins"]
    coins_xy = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
    latlon = []
    for x, y in coins_xy:
        lon, lat = _vers_lonlat(x, y)
        latlon.append([lat, lon])
    return latlon


def _couche_scenario(nom_affiche: str, couleur: str, mailles) -> folium.FeatureGroup:
    """Une couche folium : toutes les mailles inondées de ce scénario, même couleur."""
    couche = folium.FeatureGroup(name=nom_affiche)
    for maille in mailles:
        folium.Polygon(
            locations=_coins_maille_latlon(maille),
            color=None, fill=True, fill_color=couleur, fill_opacity=0.55,
            popup=nom_affiche,
        ).add_to(couche)
    return couche


def carte_folium(
    commune: Forme,
    nom_commune: str,
    mailles_par_scenario: dict[str, list[Maille]],
    sortie,
) -> None:
    """Construit la carte de l'inondation (une couche par scénario) et l'enregistre."""
    # Je centre la carte sur le milieu du contour de la commune.
    contour = [[lat, lon] for lon, lat in (_vers_lonlat(x, y) for x, y in commune[0])]
    lat_centre = sum(p[0] for p in contour) / len(contour)
    lon_centre = sum(p[1] for p in contour) / len(contour)

    carte = folium.Map(location=[lat_centre, lon_centre], zoom_start=12,
                       tiles="OpenStreetMap")
    folium.PolyLine(contour + [contour[0]], color="black", weight=2).add_to(carte)

    for cle, nom_affiche, couleur in SCENARIOS:
        mailles = mailles_par_scenario.get(cle, [])
        _couche_scenario(nom_affiche, couleur, mailles).add_to(carte)

    folium.LayerControl(collapsed=False).add_to(carte)
    carte.save(str(sortie))
    print("OK :", sortie)
