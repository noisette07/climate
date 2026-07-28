"""Programme principal : la carte de l'inondation de Marseille.

Les étapes, dans l'ordre :

  1. lire les données (commune + zones inondables)
  2. découper la commune en mailles + ranger les zones dans l'index
  3. calculer l'intensité d'inondation de chaque maille
  4. faire la carte folium (HTML)

(Les incendies, c'est l'autre script : carte_incendies.py.)

Lancer depuis le dossier src/ :  python3 main.py
"""

from pathlib import Path

import carte_inondation
import donnees
import risque
from geometrie import boite_englobante, simplifier
from grille import construire_grille

# --- Paramètres de l'étude --------------------------------------------------

COMMUNE = "Marseille"
PAS = 300.0  # côté d'une maille, en mètres (Marseille est grande : maille large)

RACINE = Path(__file__).resolve().parent.parent
DATA = RACINE / "data"
TRI = DATA / "tri_2020_sig_di_13" / "FRD_TRI_MARSEILLE"

SHP_COMMUNES = TRI / "n_tri_marseille_commune_s_013.shp"
SHP_INONDABLE = {
    "fort": TRI / "n_tri_marseille_inondable_01_01for_s_013.shp",
    "moyen": TRI / "n_tri_marseille_inondable_01_02moy_s_013.shp",
    "faible": TRI / "n_tri_marseille_inondable_01_04fai_s_013.shp",
}


def main() -> None:
    # --- Phase 1 : données ---
    # Le contour de commune est très détaillé (des dizaines de milliers de
    # points) : on l'allège à ~50 m, sans effet visible pour une grille de 300 m.
    commune = simplifier(donnees.lire_commune(SHP_COMMUNES, COMMUNE), seuil=50.0)
    boite_commune = boite_englobante(commune)
    index_par_scenario = {
        nom: risque.construire_index(donnees.lire_formes(chemin), clip=boite_commune)
        for nom, chemin in SHP_INONDABLE.items()
    }
    print(f"{COMMUNE} : index inondation construit")

    # --- Phase 2 : maillage ---
    mailles = construire_grille(commune, PAS)
    print(f"Mailles dans la commune : {len(mailles)} (pas = {PAS:.0f} m)")

    # --- Phase 3 : pour chaque scénario, les mailles inondées ---
    mailles_par_scenario = {
        nom: [m for m in mailles if risque.dans_scenario(m, index)]
        for nom, index in index_par_scenario.items()
    }
    for nom, liste in mailles_par_scenario.items():
        print(f"  scénario {nom} : {len(liste)} mailles inondées")

    # --- Phase 4 : carte interactive (HTML à la racine du dépôt) ---
    carte_inondation.carte_folium(commune, COMMUNE, mailles_par_scenario,
                                  RACINE / "carte_inondation.html")


if __name__ == "__main__":
    main()
