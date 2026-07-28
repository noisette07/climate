"""Capture les cartes HTML (folium) en images PNG, pour le README.

GitHub n'affiche pas les cartes interactives : on en fait donc une photo. Le
script ouvre chaque HTML dans un Chrome sans fenêtre, attend que les tuiles de
fond se chargent, puis prend une capture d'écran.

Lancer depuis la racine du dépôt :  python3 tools/rendu_png.py
"""

import time
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options

RACINE = Path(__file__).resolve().parent.parent
ASSETS = RACINE / "assets"

# (fichier HTML, image PNG de sortie)
CARTES = [
    ("carte_inondation.html", "carte_inondation.png"),
    ("carte_incendies.html", "carte_incendies.png"),
]


def capturer(html: Path, png: Path, taille=(1100, 900), attente=5) -> None:
    """Ouvre le HTML dans Chrome headless et enregistre une capture."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument(f"--window-size={taille[0]},{taille[1]}")
    options.add_argument("--hide-scrollbars")

    navigateur = webdriver.Chrome(options=options)
    try:
        navigateur.get(html.as_uri())
        time.sleep(attente)  # laisser le temps aux tuiles de fond de charger
        navigateur.save_screenshot(str(png))
    finally:
        navigateur.quit()
    print("OK :", png)


def main() -> None:
    ASSETS.mkdir(exist_ok=True)
    for nom_html, nom_png in CARTES:
        capturer(RACINE / nom_html, ASSETS / nom_png)


if __name__ == "__main__":
    main()
