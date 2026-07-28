"""Carte des incendies du département 13 : une couleur par commune.

Pour l'inondation je pouvais colorer maille par maille. Pour les feux, non : la
BDIFF ne dit pas OÙ ça a brûlé dans la commune, juste dans quelle commune. Donc
je change d'échelle : je colore les 119 communes du département selon leur nombre
de feux 2007-2025. Là c'est parlant (Martigues, Marseille et les communes
boisées ressortent, le reste est clair).

Je récupère les contours des communes une fois sur l'API publique
geo.api.gouv.fr (déjà en longitude/latitude) et je les garde dans
data/communes_13.geojson.

Lancer depuis src/ :  python3 carte_incendies.py
"""

import json
import urllib.request
from pathlib import Path

import folium
from branca.colormap import LinearColormap

import donnees

RACINE = Path(__file__).resolve().parent.parent
CSV_INCENDIES = RACINE / "data" / "Incendies.csv"
CACHE_COMMUNES = RACINE / "data" / "communes_13.geojson"
SORTIE = RACINE / "carte_incendies.html"

API_COMMUNES = (
    "https://geo.api.gouv.fr/departements/13/communes"
    "?fields=code,nom,contour&format=json&geometry=contour"
)


def charger_communes() -> list[dict]:
    """Renvoie les communes du 13. Depuis le cache si possible, sinon l'API."""
    if CACHE_COMMUNES.exists():
        return json.loads(CACHE_COMMUNES.read_text(encoding="utf-8"))

    print("Téléchargement des contours de communes (geo.api.gouv.fr)...")
    with urllib.request.urlopen(API_COMMUNES, timeout=30) as reponse:
        communes = json.load(reponse)
    CACHE_COMMUNES.write_text(json.dumps(communes), encoding="utf-8")
    return communes


def main() -> None:
    communes = charger_communes()
    feux_par_commune = donnees.incendies_par_commune(CSV_INCENDIES)

    # Nombre de feux par commune (0 si la commune n'apparaît pas dans la BDIFF).
    nb_feux = {c["code"]: len(feux_par_commune.get(c["code"], [])) for c in communes}
    maxi = max(nb_feux.values())
    plus_touchee = max(communes, key=lambda c: nb_feux[c["code"]])["nom"]
    print(f"{len(communes)} communes ; max {maxi} feux ({plus_touchee})")

    carte = folium.Map(location=[43.5, 5.1], zoom_start=9, tiles="OpenStreetMap")
    palette = LinearColormap(["#ffffb2", "#fd8d3c", "#bd0026"], vmin=0, vmax=maxi)
    palette.caption = "Nombre d'incendies 2007-2025 (BDIFF)"
    palette.add_to(carte)

    for commune in communes:
        n = nb_feux[commune["code"]]
        folium.GeoJson(
            commune["contour"],
            style_function=lambda _f, n=n: {
                "fillColor": palette(n), "color": "#666",
                "weight": 0.5, "fillOpacity": 0.7,
            },
            tooltip=f"{commune['nom']} : {n} feux",
        ).add_to(carte)

    carte.save(str(SORTIE))
    print("OK :", SORTIE)


if __name__ == "__main__":
    main()
